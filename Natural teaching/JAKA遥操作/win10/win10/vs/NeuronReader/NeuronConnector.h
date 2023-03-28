#pragma once
// NeuronSDK includes

// Voir si mettre un buffer
#include "stdafx.h"
#include "DataType.h"
#include "NeuronDataReader.h"
#include <iostream>
#include <iomanip>
#include <fstream>
#include <map>
#include <string>
#include <Eigen/core>
#include <Eigen/Dense>
#include <Eigen/Geometry>
#include<Eigen/StdVector>
#include <vector>

//#include "widget.h"
//#include <QApplication>
//#include <QPushButton>

using namespace std;

#define PI (3.1415926535897932346f)

#pragma comment(lib, "NeuronDataReader.lib")

class NeuronReader {
public:

	NeuronReader();
	~NeuronReader();

	/**
	*  @brief Connect to the Neuron
	*/
	bool Connect(char* IP, int port);

	/**
	* @brief Kill the connection
	*/
	void KillConnection();

	/**
	* @brief Callback functions to receive BVH data
	*/
	static void __stdcall BvhFrameDataReceived(void*, SOCKET_REF, BvhDataHeader*, float*);

	/**
	* @brief Callback functions to receive Calculation data
	*/
	static void __stdcall BvhCalcDataReceived(void*, SOCKET_REF, CalcDataHeader*, float* data);

	// Display information about the received BVH data
	void ShowBvhBoneInfo(SOCKET_REF, BvhDataHeader*, float*);
	// Display information about the received Calc data
	void ShowBvhCalcInfo(SOCKET_REF, CalcDataHeader*, float*);

	void InitializeBvhHeader();

	void MotionExport();

	//void FinalizeBvh();
	//void InitializeBvh(BvhDataHeader*, float*);
	//void BvhExport(BvhDataHeader*, float*);
	//void BvhFrameInformations();
	//void BvhMotionCopy();

	Eigen::Vector3d GetRightFore2Base() { return rightFore2Base; };
	Eigen::Vector3d GetRightShoulder2Base() { return rightShoulder2Base; };
	Eigen::Vector3d GetRightArm2Base() { return rightArm2Base; };
	Eigen::Vector3d GetRightHand2Base() { return rightHand2Base; };

	Eigen::Vector3d GetLeftFore2Base() { return leftFore2Base; };
	Eigen::Vector3d GetLeftShoulder2Base() { return leftShoulder2Base; };
	Eigen::Vector3d GetLeftArm2Base() { return leftArm2Base; };
	Eigen::Vector3d GetLeftHand2Base() { return leftHand2Base; };

	Eigen::Vector3d GetHead2Base() { return head2Base; };
	Eigen::Vector3d GenNeck2Base() { return neck2Base; };

	Eigen::Vector3d *GetLeftBones() { return leftBones; };

	bool IsConnected() { return isConnected; };

private:
	// Socket used to connect to the Neuron
	SOCKET_REF sockTCPRef;

	// See below for more information
	enum {
		BVHBoneCount = 59,
		CalcBoneCount = 21,
	};

	std::ofstream m_outfile;
	bool m_firstWrite;
	double m_initialFrame, m_currentFrame;
	int m_perJoint;
	int m_dataCount;
	string m_outFilename;
	std::map<int, std::string> m_bones;
	bool isConnected = false;

	Eigen::Vector3d rightHand2Base;
	Eigen::Vector3d rightFore2Base;
	Eigen::Vector3d rightArm2Base;
	Eigen::Vector3d rightShoulder2Base;

	Eigen::Vector3d leftHand2Base;
	Eigen::Vector3d leftFore2Base;
	Eigen::Vector3d leftArm2Base;
	Eigen::Vector3d leftShoulder2Base;

	Eigen::Vector3d head2Base;
	Eigen::Vector3d neck2Base;

	vector<Eigen::Vector3d, Eigen::aligned_allocator<Eigen::Vector3d>> rightBones;
	Eigen::Vector3d leftBones[4];
};