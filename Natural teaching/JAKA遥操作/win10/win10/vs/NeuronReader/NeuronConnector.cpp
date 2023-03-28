#include "stdafx.h"
#include "NeuronConnector.h"
#include <iostream>

NeuronReader::NeuronReader() {
	m_firstWrite = true;
	m_initialFrame = -1;
	m_dataCount = -1;
	m_outFilename = "motion.txt";
}


NeuronReader::~NeuronReader() {

}

bool NeuronReader::Connect(char* IP, int port) {

	if (sockTCPRef) {
		BRCloseSocket(sockTCPRef);
		sockTCPRef = 0;
	}

	// Clear data inside txt file
	m_outfile.open(m_outFilename, ios::out);
	m_outfile.close();

	sockTCPRef = BRConnectTo(IP, port);

	if (sockTCPRef) {
		isConnected = true;
		BRRegisterFrameDataCallback(this, BvhFrameDataReceived);
		BRRegisterCalculationDataCallback(this, BvhCalcDataReceived);


		return true;
	}

	return false;
}

void NeuronReader::KillConnection() {
	BRCloseSocket(sockTCPRef);
	//FinalizeBvh();
}

void __stdcall NeuronReader::BvhFrameDataReceived(void* customedObj, SOCKET_REF sender, BvhDataHeader* header, float* data) {

	NeuronReader* pthis = (NeuronReader*)customedObj;
	pthis->ShowBvhBoneInfo(sender, header, data);
}

void __stdcall NeuronReader::BvhCalcDataReceived(void* customedObj, SOCKET_REF sender, CalcDataHeader* header, float* data) {
	NeuronReader* pthis = (NeuronReader*)customedObj;
	pthis->ShowBvhCalcInfo(sender, header, data);
}


void NeuronReader::ShowBvhCalcInfo(SOCKET_REF sender, CalcDataHeader* header, float* data) {
	int rightIdx[] = { 7, 8, 9, 10 };
	int leftIdx[] = { 11,12,13,14 };
	int headIdx[] = { 15, 16, 17 };
	string rightInfo[] = {
		"Right Shoulder, Bone index: 7" ,
		"Right Arm, Bone index: 8",
		"Right Fore Arm, Bone index: 9",
		"Right Hand, Bone index: 10" };
	string leftInfo[] = {
		"Right Shoulder, Bone index: 7" ,
		"Right Arm, Bone index: 8",
		"Right Fore Arm, Bone index: 9",
		"Right Hand, Bone index: 10" };
	string headInfo[] = {
		"Head, Bone index: 15" ,
		"Neck, Bone index: 16",
		"Spine 3, Bone index: 17" };
	cout << "------ Frame: " << header->FrameIndex << " ------" << endl;
	cout << "------ Bone Info ------" << endl;

	vector<Eigen::Vector3d, Eigen::aligned_allocator<Eigen::Vector3d>> rightVectorList(4);
	vector<Eigen::Vector3d, Eigen::aligned_allocator<Eigen::Vector3d>> leftVectorList(4);
	vector<Eigen::Vector3d, Eigen::aligned_allocator<Eigen::Vector3d>> headVectorList(4);

	for (int i = 0; i < 4; ++i) {
		//cout << rightInfo[i] << endl;
		rightVectorList[i](0) = data[16 * rightIdx[i] + 0]; // x
		rightVectorList[i](1) = -data[16 * rightIdx[i] + 2]; // y
		rightVectorList[i](2) = data[16 * rightIdx[i] + 1]; // z
		//cout << leftInfo[i] << endl;
		leftVectorList[i](0) = data[16 * leftIdx[i] + 0]; // x
		leftVectorList[i](1) = -data[16 * leftIdx[i] + 2]; // y
		leftVectorList[i](2) = data[16 * leftIdx[i] + 1]; // z
	}
	rightShoulder2Base = rightVectorList[0];
	rightArm2Base = rightVectorList[1] - rightVectorList[0];
	rightFore2Base = rightVectorList[2] - rightVectorList[0];
	rightHand2Base = rightVectorList[3] - rightVectorList[0];

	leftShoulder2Base = leftVectorList[0];
	leftArm2Base = leftVectorList[1] - leftVectorList[0];
	leftFore2Base = leftVectorList[2] - leftVectorList[0];
	leftHand2Base = leftVectorList[3] - leftVectorList[0];

	//cout << "Hand: " << -rightHand2Base[0] << " " << rightHand2Base[2] << " " << rightHand2Base[1] << endl;
	//cout << "Arm: " << -rightArm2Base[0] << " " << rightArm2Base[2] << " " << rightArm2Base[1] << endl;

	for (int i = 0; i < 3; ++i) {
		//cout << headInfo[i] << endl;
		headVectorList[i](0) = data[16 * headIdx[i] + 0]; // x
		headVectorList[i](1) = -data[16 * headIdx[i] + 2]; // y
		headVectorList[i](2) = data[16 * headIdx[i] + 1]; // z
	}
	head2Base = headVectorList[0] - headVectorList[2];
	neck2Base = headVectorList[1] - headVectorList[2];

#ifdef DATA_OUTPUT
	Export motion data, append at the end
	m_outfile.open(m_outFilename, ios::app);
	if (!m_outfile.fail()) {
		m_outfile << header->FrameIndex << " ";
		m_outfile << rightArm2Base[0] << " " << rightArm2Base[1] << " " << rightArm2Base[2] << " ";
		m_outfile << rightFore2Base[0] << " " << rightFore2Base[1] << " " << rightFore2Base[2] << " ";
		m_outfile << rightHand2Base[0] << " " << rightHand2Base[1] << " " << rightHand2Base[2] << " ";

		m_outfile << leftArm2Base[0] << " " << leftArm2Base[1] << " " << leftArm2Base[2] << " ";
		m_outfile << leftFore2Base[0] << " " << leftFore2Base[1] << " " << leftFore2Base[2] << " ";
		m_outfile << leftHand2Base[0] << " " << leftHand2Base[1] << " " << leftHand2Base[2] << " ";

		m_outfile << "\n";
		m_outfile.close();
	}
#endif // DATA_OUTPUT

}

void NeuronReader::MotionExport() {

}

void NeuronReader::ShowBvhBoneInfo(SOCKET_REF sender, BvhDataHeader* header, float* data) {

	//int rightIdx[] = { 37, 38, 39, 40 };
	int rightIdx[] = { 12, 13, 14, 15, 16 };
	string rightInfo[] = {
		"Temp, Bone idex: 12" ,
		"Right Shoulder, Bone index: 13" ,
		"Right Arm, Bone index: 14",
		"Right Fore Arm, Bone index: 15",
		"Right Hand, Bone index: 16" };
	cout << "------ Frame: " << header->FrameIndex << " ------" << endl;
	cout << "With Displacement: " << (int)header->WithDisp << endl;
	cout << "With Reference: " << (int)header->WithReference << endl; // Shoule be 0 
	cout << "------ Bone Info ------" << endl;
	if (header->WithDisp) {
		vector<Eigen::Isometry3d> TList(4);
		for (int i = 1; i < 5; ++i) {
			cout << rightInfo[i] << endl;
			vector<float> ea(6);
			vector<float> eaPrev(6);
			for (int j = 0; j < 6; ++j) {
				ea[j] = data[6 * rightIdx[i] + j]; //  Y X Z
				eaPrev[j] = data[6 * rightIdx[i - 1] + j]; //  Y X Z
				cout << ea[j] << " ";
			}
			cout << endl;
			Eigen::Matrix3d R;

			R = Eigen::AngleAxisd(eaPrev[3], Eigen::Vector3d::UnitY()) *
				Eigen::AngleAxisd(eaPrev[4], Eigen::Vector3d::UnitX()) *
				Eigen::AngleAxisd(eaPrev[5], Eigen::Vector3d::UnitZ());

			Eigen::Vector3d t(ea[0], ea[1], ea[2]);
			cout << "Translation Vector: " << endl;
	
			Eigen::Isometry3d T(R);
			T.pretranslate(t);

			TList[i - 1] = T;

		}

		TList.clear();

	}
	else {
		for (int i = 0; i < 4; ++i) {
			cout << rightInfo[i] << endl;
			for (int j = 0; j < 3; ++j) {
				cout << data[3 + 3 * rightIdx[i] + j] << " ";
			}
			cout << endl;
		}
	}

}





// Copy the template of the Neuron bvh header (see appendix A in the doc)
void NeuronReader::InitializeBvhHeader() {
	m_outfile.open("test.bvh");

	if (m_outfile.is_open()) {
		std::ifstream bvh_header_template("bvh_header_template.bvh");

		if (bvh_header_template.is_open()) {

			std::string line;

			// Special case : we need to eliminate the XYZ position
			if (m_perJoint == 3) {
				bool isRoot = true;

				while (std::getline(bvh_header_template, line)) {
					// For the root, we leave the 6 cahnnels
					if (!strncmp(line.c_str(), "JOINT", strlen("JOINT")))
						isRoot = false;

					// If it's the channel line AND it's not the root
					// We write a modified channel line
					if (!strncmp(line.c_str(), "CHANNELS", strlen("CHANNELS")) && !isRoot)
						m_outfile << "CHANNELS 3 Yrotation Xrotation Zrotation\n";

					// Else, just ouput the line
					else
						m_outfile << line << '\n';
				}
			}

			else {
				while (std::getline(bvh_header_template, line))
					m_outfile << line << "\n";
			}
			bvh_header_template.close();

		}

		else {
			std::cout << "Error opening bvh_header_template.bvh" << std::endl;
		}

		m_outfile.close();
	}

	else {
		std::cout << "Error opening test.bvh" << std::endl;
	}


}