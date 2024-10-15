#include "json.hpp"
#include <iostream>
#include <bits/stdc++.h>
#include <fstream>
#include <sstream>
#include <random>
#include <chrono>
#include <cmath>

using namespace std;
using json = nlohmann::json;

int getRandomInt(int a, int b) {
    random_device rd;  // Seed
    mt19937 gen(rd()); // Mersenne Twister generator
    uniform_int_distribution<> dis(a, b); // Uniform distribution in [a, b]
    return dis(gen);
}

class DeterministicNetwork {
    set<tuple<string, string>> edges;
    set<string> initialInfectedNodes;
    set<string> nodes;
    unordered_map<string, vector<string>> incomingEdges;
    unordered_map<string, vector<string>> outgoingEdges;
    set<string> vaccinatedNodes;

    public: 
    set<string> getInitialInfectedNodes() const {
        return initialInfectedNodes;
    }

    set<tuple<string, string>> getEdges() const {
        return edges;
    }

    void addNode(string node) {
        nodes.insert(node);
    }
    void addInitialInfectedNode(string node) {
        initialInfectedNodes.insert(node);
        addNode(node);
    }
    void addInitialInfectedNodes(set<string> infectedNodes) {
        initialInfectedNodes = infectedNodes;
        nodes.insert(infectedNodes.begin(), infectedNodes.end());
    }
    void addNeighbours(string u, string v) {
        incomingEdges[v].push_back(u);
        outgoingEdges[u].push_back(v);
    }
    // edge from u to v
    void addEdge(string u, string v) {
        edges.insert(make_tuple(u, v));
        nodes.insert(u);
        nodes.insert(v);
        addNeighbours(u, v);
    }
    void vaccinateNode(string node) {
        vaccinatedNodes.insert(node);
    }
    void clearVaccinatedNodes() {
        vaccinatedNodes.clear();
    }
    set<string> vaccinateNodeAndCheck(string node) {
        vaccinatedNodes.insert(node);

        set<string> infected = initialInfectedNodes;
        queue<string> toVisit;

        for (const auto& node : initialInfectedNodes) {
            toVisit.push(node);
        }

        while (!toVisit.empty()) {
            string current = toVisit.front();
            toVisit.pop();
            for (const auto& neighbor : outgoingEdges[current]) {
                if (infected.find(neighbor) == infected.end() && vaccinatedNodes.find(neighbor) == vaccinatedNodes.end()) {
                    infected.insert(neighbor);
                    toVisit.push(neighbor);
                }
            }
        }
        // temoporarily vaccinated so remove from vaccinated set at the end
        vaccinatedNodes.erase(node);

        set<string> uninfected;
        set_difference(nodes.begin(), nodes.end(), infected.begin(), infected.end(),
                   inserter(uninfected, uninfected.begin()));
        return uninfected;
    }
    set<string> vaccinateNodesAndCheck(set<string> vaccinatednodes) {
        for (auto node : vaccinatednodes) vaccinatedNodes.insert(node);

        set<string> infected = initialInfectedNodes;
        queue<string> toVisit;

        for (const auto& node : initialInfectedNodes) {
            toVisit.push(node);
        }

        while (!toVisit.empty()) {
            string current = toVisit.front();
            toVisit.pop();
            for (const auto& neighbor : outgoingEdges[current]) {
                if (infected.find(neighbor) == infected.end() && vaccinatedNodes.find(neighbor) == vaccinatedNodes.end()) {
                    infected.insert(neighbor);
                    toVisit.push(neighbor);
                }
            }
        }
        // temoporarily vaccinated so remove from vaccinated set at the end
        for (auto node : vaccinatednodes) vaccinatedNodes.erase(node);

        set<string> uninfected;
        set_difference(nodes.begin(), nodes.end(), infected.begin(), infected.end(),
                   inserter(uninfected, uninfected.begin()));
        return uninfected;
    }
    set<string> getOutgoingEdgeNodes(string node) {
        return set<string> (outgoingEdges[node].begin(), outgoingEdges[node].end());
    }
    set<string> getIncomingEdgeNodes(string node) {
        return set<string> (incomingEdges[node].begin(), incomingEdges[node].end());
    }
};

class LinearThresholdNetwork {
    set<tuple<string, string, double>> edges;
    set<string> initialInfectedNodes;
    set<string> nodes;
    unordered_map<string, vector<tuple<string, double>>> incomingEdges;
    unordered_map<string, vector<tuple<string, double>>> outgoingEdges;
    int numInstances;
    int numVaccines;
    vector<DeterministicNetwork> deterministicInstances;
    set<string> vaccinatedNodes;
    vector<string> greedySolution;

    public:

    // Function to convert deterministic instances into JSON format
    json toJSON() {
        json j;
        for (auto& dn : deterministicInstances) {
            json instance;
            instance["infected_nodes"] = dn.getInitialInfectedNodes();
            for (const auto& edge : dn.getEdges()) {
                instance["edges"].push_back({get<0>(edge), get<1>(edge)});
            }
            j.push_back(instance);
        }
        return j;
    }

    // Saving deterministic instances to a JSON file
    void saveInstancesToJson(const std::string& filename) {
        json j = toJSON();
        std::ofstream file(filename);
        file << j.dump(4);  // Pretty print with 4 spaces of indentation
        file.close();
    }

    void addNode(string node) {
        nodes.insert(node);
    }
    set<string> getNodes() {
        return nodes;
    }
    void addInitialInfectedNode(string node) {
        initialInfectedNodes.insert(node);
        addNode(node);
    }
    void addInitialInfectedNodes(set<string> infectedNodes) {
        initialInfectedNodes = infectedNodes;
        nodes.insert(infectedNodes.begin(), infectedNodes.end());
    }
    void addNeighbours(string u, string v, double b_uv) {
        incomingEdges[v].push_back(make_tuple(u, b_uv));
        outgoingEdges[u].push_back(make_tuple(v, b_uv));
    }
    // edge directed from u to v
    void addEdge(string u, string v, double b_uv) {
        edges.insert(make_tuple(u, v, b_uv));
        nodes.insert(u);
        nodes.insert(v);
        addNeighbours(u, v, b_uv);
    }
    bool isValidNetwork() {
        for (const auto& elem : incomingEdges) {
            vector<tuple<string, double>> nbrs = elem.second;
            double sum = 0;
            for (auto nbr : nbrs) {
                sum += get<1>(nbr);
                if (sum > 1) return false;
            }
        }
        return true;
    }
    void vaccinateNode(string node) {
        vaccinatedNodes.insert(node);
    }
    void setNumInstances(int n) {
        numInstances = n;
    }
    void setNumVaccines(int n) {
        numVaccines = n;
    }
    int getNumInstances() {
        return numInstances;
    }
    int getNumVaccines() {
        return numVaccines;
    }
    vector<DeterministicNetwork> getDeterministicInstances() {
        random_device rd;  
        mt19937 gen(rd());
        uniform_real_distribution<> dis(0, 1);

        for (int i = 0; i < numInstances; i++) {
            DeterministicNetwork dn;
            dn.addInitialInfectedNodes(initialInfectedNodes);
            for (const auto& elem : incomingEdges) {
                vector<tuple<string, double>> nbrs = elem.second;
                double randomValue = dis(gen);
                double sum = 0;
                int selectedIndex = -1;
                for (int j = 0; j < nbrs.size(); j++) {
                    sum += get<1>(nbrs[j]);
                    if (randomValue < sum) {
                        selectedIndex = j;
                        break;
                    }
                }
                if (selectedIndex > -1) dn.addEdge(get<0>(nbrs[selectedIndex]), elem.first);
                else dn.addNode(elem.first);
            }
            deterministicInstances.push_back(dn);
        }
        return deterministicInstances;
    }
    vector<string> getInitialKNodes() {
        auto start = std::chrono::high_resolution_clock::now();
        set<string> uninfectedNodes;
        set_difference(nodes.begin(), nodes.end(), initialInfectedNodes.begin(), initialInfectedNodes.end(),
                inserter(uninfectedNodes, uninfectedNodes.begin()));
        vector<string> availableNodes(uninfectedNodes.begin(), uninfectedNodes.end());
        for (int i = 0; i < min(numVaccines, (int)nodes.size()); i++) {
            string maxSavedNode = availableNodes[0];
            int prevSavedSum = 0;
            for (int j = 0; j < availableNodes.size(); j++) {
                string avnode = availableNodes[j];
                int savedSum = 0;
                for (auto& dn : deterministicInstances) {
                    set<string> savedNodes = dn.vaccinateNodeAndCheck(avnode);
                    savedSum += savedNodes.size();
                }
                if (savedSum > prevSavedSum) {
                    prevSavedSum = savedSum;
                    maxSavedNode = avnode;
                }
                uninfectedNodes = set<string>(availableNodes.begin(), availableNodes.end());
            }
            availableNodes.erase(remove(availableNodes.begin(), availableNodes.end(), maxSavedNode), availableNodes.end());
            for (auto& dn : deterministicInstances) dn.vaccinateNode(maxSavedNode);
            vaccinateNode(maxSavedNode);
            
        }
        vector<string> res(vaccinatedNodes.begin(), vaccinatedNodes.end());
        vaccinatedNodes.clear();
        for (auto& dn : deterministicInstances) dn.clearVaccinatedNodes();
        greedySolution = res;
        int initialSavedSum = 0;
        for (auto& dn : deterministicInstances) {
            set<string> savedNodes = dn.vaccinateNodesAndCheck(set<string> (greedySolution.begin(), greedySolution.end()));

            initialSavedSum += savedNodes.size();
        }
        cout << (nodes.size() * numInstances - initialSavedSum) << endl;
        auto end = std::chrono::high_resolution_clock::now();

        // Calculate the duration
        std::chrono::duration<double> duration = end - start;

        // Print the total time in seconds
        cout << duration.count() << endl;
        return res;
    }
};

int main (int argc, char* argv[]) {

    if (argc != 2) {
        cerr << "Usage: " << argv[0] << " <linearThresholdModelFileName>" << endl;
        return 1;
    }
    ifstream file1(argv[1]);
    if (!file1.is_open()) {
        cerr << "Error opening file: " << argv[1] << endl;
        return 1;
    }
    LinearThresholdNetwork diseaseSpreadingNetwork;

    string line;
    bool foundInfectedNode = false;
    bool foundNumInstances = false;
    bool foundNumVaccines = false;
    while (getline(file1, line)) {
        istringstream iss(line);
        string type;
        iss >> type;
        if (type == "INFECTED_NODE") {
            string node;
            iss >> node;
            diseaseSpreadingNetwork.addInitialInfectedNode(node);
            foundInfectedNode = true;
            continue;
        }
        // edge directed from u to v
        else if (type == "EDGE") {
            string u, v, b_uv;
            iss >> u >> v >> b_uv;
            double f_b_uv = stof(b_uv);
            diseaseSpreadingNetwork.addEdge(u, v, f_b_uv);
        }
        else if (type == "NUM_INSTANCES") {
            string n;
            iss >> n;
            int i_n = stoi(n);
            diseaseSpreadingNetwork.setNumInstances(i_n);
            foundNumInstances = true;
        }
        else if (type == "NUM_VACCINES") {
            string n;
            iss >> n;
            int i_n = stoi(n);
            diseaseSpreadingNetwork.setNumVaccines(i_n);
            foundNumVaccines = true;
        }
        else if (type == "NODE") {
            string n;
            iss >> n;
            diseaseSpreadingNetwork.addNode(n);
        }
        else {
            cerr << type << endl;
            cerr << "Invalid input" << endl;
            return 1;
        }
    }
    file1.close();
    if (!(foundInfectedNode && foundNumInstances && foundNumVaccines) || !diseaseSpreadingNetwork.isValidNetwork()) {
        if (!foundInfectedNode) cerr << "not found infected nodes\n";
        else if (!foundNumInstances) cerr << "not found num instances\n";
        else if (!foundNumVaccines) cerr << "not found num vaccines\n";
        else cerr << "Invalid network: Weight of incoming edges exceeds 1\n";
        return 1;
    }
    // auto start = std::chrono::high_resolution_clock::now();
    diseaseSpreadingNetwork.getDeterministicInstances();
    string filename = "greedy_deterministicInstances_" +  to_string(diseaseSpreadingNetwork.getNodes().size()) + "_" + to_string(diseaseSpreadingNetwork.getNumVaccines()) + "_" + to_string(diseaseSpreadingNetwork.getNumInstances()) + ".json";
    diseaseSpreadingNetwork.saveInstancesToJson(filename);
    diseaseSpreadingNetwork.getInitialKNodes();

    // auto end = std::chrono::high_resolution_clock::now();

    // // Calculate the duration
    // std::chrono::duration<double> duration = end - start;

    // Print the total time in seconds
    // cout << duration.count() << endl;
}
