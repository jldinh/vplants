#include <iostream>
#include "smithModel.hpp"

using namespace std;

void Model::run(){
    std::cout << "Model::run";
}

int main(){
    cout << "main";
    Model m = Model();
    m.run();
    return 0;
}
