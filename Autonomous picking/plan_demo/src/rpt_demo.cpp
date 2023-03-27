//
// Created by msi on 2022/3/19.
//

#include <scene.hpp>

int main() {
    Scene scene;
    scene.loadFromFile("/home/msi/CLionProjects/RPT/test/test_collision_check.json");

    int N = 0;
    std::cin >> N;
    std::vector<std::vector<std::vector<DataType>>>
            testJointValues(N, std::vector<std::vector<DataType>>(6, std::vector<DataType>(1)));
    for (int i = 0; i < N; ++i) {
        for (int j = 0; j < 6; ++j) {
            std::cin >> testJointValues[i][j][0];
        }
    }
    std::vector<std::string> jointNames(6);
    for (int i = 0; i < 6; ++i) {
        jointNames.at(i) = "joint_" + std::to_string(i + 1);
    }
    std::ofstream file("/home/msi/result.txt");
    if (!file.is_open()) {
        throw std::runtime_error("cannot open result file");
    }

    int i = 0;
//    std::reverse(testJointValues.begin(), testJointValues.end());
    double total_cost = 0;
    for (const auto &jVals: testJointValues) {
//    for (int j = 0; j < 2; ++j) {
//        auto jVals = testJointValues[1];
        scene.setRobotConfiguration(jointNames, jVals);
//        for (auto &val: jVals)
//            fmt::print("{:.3f}, ", val[0]);
//        fmt::print("\n");
        plf::nanotimer timer;
        timer.start();
        bool isCollision = true;
//        if (i == 1)
        isCollision = scene.isCollision();
        auto elapsed = timer.get_elapsed_ms();
//        fmt::print("statu {}\n", isCollision);
        file << fmt::format("{} {:.6}", isCollision, elapsed) << std::endl;
        i++;
        total_cost += elapsed;
    }
    fmt::print("avg. {:.6f} ms\n", total_cost / N);
    file.close();
    std::cout << "[test_collision_check] end" << std::endl;
    return 0;
}