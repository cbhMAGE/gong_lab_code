#include "stdafx.h"
#include <iostream>
#include "NeuronConnector.h"

#include <thread>	
#include <future>	
#include <conio.h>	
#include <iostream>
#include <stdlib.h>
#include <stdio.h>
#include <GL/glut.h>
#include <GL/freeglut_ext.h>
#include <string>
#include <cstring>
#include <WS2tcpip.h>
#include <WinSock2.h>						
#include <Windows.h>
#include <vector>
#include <ctime>
#include "JointAngleCalc.h"

#include <time.h>
#pragma comment(lib, "ws2_32.lib") 
// ------------------------------------------------------------

using namespace std;

// Select neuron port
#define BVH_PORT 7001
#define CAL_PORT 7003

const int len_double = sizeof(double);
typedef union doubletochar_8
{
	double num_double;
	char num_char[len_double];
}doubletochar;
SOCKET serviceSocket;
sockaddr_in revClientAddr;
SOCKET recvClientSocket = INVALID_SOCKET;	//初始化一个接受的客户端socket


NeuronReader NCon;

// Asynchronously check if Esc is pressed
bool isEsc() {
	char ch = _getch();
	if (ch == 27)
		return true;
	return false;
}

float angle = 0.0f;
float z = 0.0f;
float depth = 30.0f;

// Camera initial settings
static float   camera_yaw = 0.0f;
static float   camera_pitch = -30.0f;
static float   camera_distance = 10.0f;
static float   camera_x = 0.0f;
static float   camera_y = 0.0f;

static int     drag_mouse_r = 0;
static int     drag_mouse_l = 0;
static int     drag_mouse_m = 0;
static int     last_mouse_x, last_mouse_y;

double isReady = 0.0;


void changeSize(int w, int h) {

	// Prevent a divide by zero, when window is too short
	// (you cant make a window of zero width).
	if (h == 0)
		h = 1;

	float ratio = w * 1.0 / h;

	// Set the viewport to be the entire window
	glViewport(0, 0, w, h);

	// Use the Projection Matrix
	glMatrixMode(GL_PROJECTION);

	// Reset Matrix
	glLoadIdentity();

	// Set the correct perspective.
	gluPerspective(45.0f, ratio, 0.1f, 500.0f);

	//// Reset transformations
	//glLoadIdentity();
	// Set the camera
	gluLookAt(0.0f, 0.0f, depth,
		0.0f, 0.0f, 0.0f,
		0.0f, 1.0f, 0.0f);                 // From z-axis

										   // Get Back to the Modelview
	glMatrixMode(GL_MODELVIEW);
}




void renderScene(void) {
	//glClearColor(0.5f, 0.5f, 0.5f, 1.0f); // Backgound color
	// Clear Color and Depth Buffers
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT | GL_STENCIL_BUFFER_BIT);

	glMatrixMode(GL_MODELVIEW);
	glLoadIdentity(); // Reset viewpoint
	glTranslatef(-camera_x, 0.0, 0.0);
	glTranslatef(0.0, -camera_y, 0.0);
	glTranslatef(0.0, 0.0, -camera_distance);

	//glRotatef(-camera_yaw, 1.0, 0.0, 0.0);
	//glRotatef(-camera_pitch, 0.0, 1.0, 0.0);
	glRotatef(-camera_pitch, 1.0, 0.0, 0.0);
	glRotatef(-camera_yaw, 0.0, 1.0, 0.0);

	//glRotatef(angle, 0.0f, 1.0f, 0.0f);

	/**
	* @brief Draw chess board
	*/
	float  size = 5.0f, goundHeight = -8.0f;
	int  num_x = 10, num_z = 10;
	double  ox, oz;
	glBegin(GL_QUADS);

	glNormal3d(0.0, 1.0, 0.0);
	ox = -(num_x * size) / 2;
	for (int x = 0; x<num_x; x++, ox += size)
	{
		oz = -(num_z * size) / 2;
		for (int z = 0; z<num_z; z++, oz += size)
		{
			if (((x + z) % 2) == 0)
				glColor3f(1.0, 1.0, 1.0);
			else
				glColor3f(0.8, 0.8, 0.8);
			glVertex3d(ox, goundHeight, oz);
			glVertex3d(ox, goundHeight, oz + size);
			glVertex3d(ox + size, goundHeight, oz + size);
			glVertex3d(ox + size, goundHeight, oz);
		}
	}

	glEnd();

	/**
	* @brief Draw bones
	*/
	vector<double> endEffector(3, 0);
	if (NCon.IsConnected()) {

		glPointSize(10);
		//glBegin(GL_LINE_STRIP);
		double scaleRate = 20;

		glLineWidth(4);
		glBegin(GL_LINE_STRIP);
		//glColor3f(0.0, 1.0, 0.0);
		glColor3f(1.0, 0.0, 0.0);
		glVertex3f(0.0f, 0.0f, 0.0f);
		//glVertex3d(NCon.GetRightShoulder2Base()[0] * scaleRate, NCon.GetRightShoulder2Base()[1] * scaleRate, NCon.GetRightShoulder2Base()[2] * scaleRate);
		glVertex3d(NCon.GetRightArm2Base()[0] * scaleRate, NCon.GetRightArm2Base()[1] * scaleRate, NCon.GetRightArm2Base()[2] * scaleRate);
		glVertex3d(NCon.GetRightFore2Base()[0] * scaleRate, NCon.GetRightFore2Base()[1] * scaleRate, NCon.GetRightFore2Base()[2] * scaleRate);
		glVertex3d(NCon.GetRightHand2Base()[0] * scaleRate, NCon.GetRightHand2Base()[1] * scaleRate, NCon.GetRightHand2Base()[2] * scaleRate);
		glEnd();

		glBegin(GL_LINE_STRIP);
		glColor3f(1.0, 0.0, 0.0);
		glVertex3f(0.0f, 0.0f, 0.0f);
		//glVertex3d(NCon.GetLeftShoulder2Base()[0] * scaleRate, NCon.GetLeftShoulder2Base()[1] * scaleRate, NCon.GetLeftShoulder2Base()[2] * scaleRate);
		glVertex3d(NCon.GetLeftArm2Base()[0] * scaleRate, NCon.GetLeftArm2Base()[1] * scaleRate, NCon.GetLeftArm2Base()[2] * scaleRate);
		glVertex3d(NCon.GetLeftFore2Base()[0] * scaleRate, NCon.GetLeftFore2Base()[1] * scaleRate, NCon.GetLeftFore2Base()[2] * scaleRate);
		glVertex3d(NCon.GetLeftHand2Base()[0] * scaleRate, NCon.GetLeftHand2Base()[1] * scaleRate, NCon.GetLeftHand2Base()[2] * scaleRate);
		glEnd();

		glPointSize(7);
		glBegin(GL_POINTS);
		glColor3f(1.0, 0.0, 0.0);
		//glVertex3d(NCon.GetRightShoulder2Base()[0] * scaleRate, NCon.GetRightShoulder2Base()[1] * scaleRate, NCon.GetRightShoulder2Base()[2] * scaleRate);
		glVertex3d(NCon.GetRightArm2Base()[0] * scaleRate, NCon.GetRightArm2Base()[1] * scaleRate, NCon.GetRightArm2Base()[2] * scaleRate);
		glVertex3d(NCon.GetRightFore2Base()[0] * scaleRate, NCon.GetRightFore2Base()[1] * scaleRate, NCon.GetRightFore2Base()[2] * scaleRate);
		glVertex3d(NCon.GetRightHand2Base()[0] * scaleRate, NCon.GetRightHand2Base()[1] * scaleRate, NCon.GetRightHand2Base()[2] * scaleRate);
		//glVertex3d(NCon.GetLeftShoulder2Base()[0] * scaleRate, NCon.GetLeftShoulder2Base()[1] * scaleRate, NCon.GetLeftShoulder2Base()[2] * scaleRate);
		glVertex3d(NCon.GetLeftArm2Base()[0] * scaleRate, NCon.GetLeftArm2Base()[1] * scaleRate, NCon.GetLeftArm2Base()[2] * scaleRate);
		glVertex3d(NCon.GetLeftFore2Base()[0] * scaleRate, NCon.GetLeftFore2Base()[1] * scaleRate, NCon.GetLeftFore2Base()[2] * scaleRate);
		glVertex3d(NCon.GetLeftHand2Base()[0] * scaleRate, NCon.GetLeftHand2Base()[1] * scaleRate, NCon.GetLeftHand2Base()[2] * scaleRate);

		glVertex3d(NCon.GetHead2Base()[0] * scaleRate, NCon.GetHead2Base()[1] * scaleRate, NCon.GetHead2Base()[2] * scaleRate);
		glVertex3d(NCon.GenNeck2Base()[0] * scaleRate, NCon.GenNeck2Base()[1] * scaleRate, NCon.GenNeck2Base()[2] * scaleRate);
		glEnd();

		// Display coordinate
		glPointSize(3);
		glBegin(GL_POINTS);
		glColor3f(1.0f, 1.0f, 1.0f);
		glVertex3f(0.0f, 0.0f, 0.0f);
		glColor3f(1.0f, 0.0f, 0.0f);
		glVertex3f(10.0f, 0.0f, 0.0f); // Red -> x direction
		glColor3f(0.0f, 1.0f, 0.0f);
		glVertex3f(0.0f, 10.0f, 0.0f); // Green -> y direction
		glColor3f(0.0f, 0.0f, 1.0f);
		glVertex3f(0.0f, 0.0f, 10.0f); // Blue -> z direction
		glEnd();

		endEffector[0] = NCon.GetRightHand2Base()[0];
		endEffector[1] = NCon.GetRightHand2Base()[1];
		endEffector[2] = NCon.GetRightHand2Base()[2];
	}

	// Select data to send by socket
#if 1
	vector<double> data2sent(4);
	data2sent[0] = isReady;
	for (int i = 0; i < 3; ++i)
		data2sent[i + 1] = endEffector[i];
#else
	cout << "Start joint angle calculation." << endl;
	vector<double> jointAngle;
	jointAngle = guanjiejiao(-NCon.GetRightHand2Base()[0], NCon.GetRightHand2Base()[2], NCon.GetRightHand2Base()[1], \
		- NCon.GetRightArm2Base()[0], NCon.GetRightArm2Base()[2], NCon.GetRightArm2Base()[1]);

	vector<double> data2sent(jointAngle);
	for (double j : jointAngle)
		cout << j << " ";
	cout << endl;
#endif


	cout << "recv." << endl;

	char recvBuf[100];
	int reLen = recv(recvClientSocket, recvBuf, strlen(recvBuf), 0);
	//recvBuf[reLen] = '\0';
	if (SOCKET_ERROR == reLen) {
		cout << "receive failed." << endl;
	}

	doubletochar num;
	int count = 0;
	while (count < data2sent.size())
	{
		char send_arr[len_double];
		num.num_double = data2sent[count];
		for (int i = len_double - 1; i >= 0; --i)//小端模式：低字节在低位，高字节在高地址
		{
			send_arr[len_double - 1 - i] = num.num_char[i];
		}
		int sLen = send(recvClientSocket, send_arr, sizeof(send_arr), 0);
		if (SOCKET_ERROR == sLen) {
			cout << "send failed." << endl;
		}
		count++;
	}
	// *************
	for (double i : data2sent)
		cout << i << " ";
	cout << endl;



	glutSwapBuffers();
}

// Keys function defination
void processNormalKeys(unsigned char key, int x, int y) {

	if (key == 'w')
		depth += 5.0f;
	if (key == 's')
		depth -= 5.0f;
	// Reset view
	if (key == 'b') {
		camera_yaw = 0.0f;
		camera_pitch = -30.0f;
		camera_distance = 10.0f;
		camera_x = 0.0f;
		camera_y = 0.0f;
	}
	if (key == 'r') {
		isReady = 1000.0;
	}
	if (key == 't') {
		isReady = 0.0;
	}
	if (key == 27)
		exit(0);
}

// Mouse function defination
void  mouse(int button, int state, int mx, int my)
{
	if ((button == GLUT_LEFT_BUTTON) && (state == GLUT_DOWN))
		drag_mouse_l = 1;
	else if ((button == GLUT_LEFT_BUTTON) && (state == GLUT_UP))
		drag_mouse_l = 0;

	if ((button == GLUT_RIGHT_BUTTON) && (state == GLUT_DOWN))
		drag_mouse_r = 1;
	else if ((button == GLUT_RIGHT_BUTTON) && (state == GLUT_UP))
		drag_mouse_r = 0;

	if ((button == GLUT_MIDDLE_BUTTON) && (state == GLUT_DOWN))
		drag_mouse_m = 1;
	else if ((button == GLUT_MIDDLE_BUTTON) && (state == GLUT_UP))
		drag_mouse_m = 0;

	glutPostRedisplay();

	last_mouse_x = mx;
	last_mouse_y = my;
}


void  motion(int mx, int my)
{
	if (drag_mouse_r)
	{

		camera_yaw -= (mx - last_mouse_x) * 1.0;
		if (camera_yaw < 0.0)
			camera_yaw += 360.0;
		else if (camera_yaw > 360.0)
			camera_yaw -= 360.0;

		camera_pitch -= (my - last_mouse_y) * 1.0;
		if (camera_pitch < -90.0)
			camera_pitch = -90.0;
		else if (camera_pitch > 90.0)
			camera_pitch = 90.0;
	}
	if (drag_mouse_l)
	{

		camera_y += (my - last_mouse_y) * 0.1;
		camera_x -= (mx - last_mouse_x) * 0.1;

	}

	last_mouse_x = mx;
	last_mouse_y = my;

	glutPostRedisplay();
}

void mouseWheel(int button, int dir, int x, int y)
{
	double roolSpeed = 3.0;

	if (dir > 0)
	{
		camera_distance += roolSpeed;
	}
	else
	{
		camera_distance -= roolSpeed;
	}
	if (camera_distance < 1.0)
		camera_distance = 1.0;

	return;
}

int mainWindow, subWindow1;
#define DEFAULT_BUFLEN 512
#define DEFAULT_PORT "5000"
int main(int argc, char **argv) {
	// Check if ESC key is pressed asynchronously
	future<bool> ret = async(&isEsc);

	WSADATA wsaData;
	int iResult;

	SOCKET ListenSocket = INVALID_SOCKET;
	//SOCKET recvClientSocket = INVALID_SOCKET;

	struct addrinfo *result = NULL;
	struct addrinfo hints;

	int iSendResult;
	char recvbuf[DEFAULT_BUFLEN];
	int recvbuflen = DEFAULT_BUFLEN;

	// Initialize Winsock
	iResult = WSAStartup(MAKEWORD(2, 2), &wsaData);
	if (iResult != 0) {
		printf("WSAStartup failed with error: %d\n", iResult);
		return 1;
	}

	ZeroMemory(&hints, sizeof(hints));
	hints.ai_family = AF_INET;
	hints.ai_socktype = SOCK_STREAM;
	hints.ai_protocol = IPPROTO_TCP;
	hints.ai_flags = AI_PASSIVE;

	// Resolve the server address and port
	iResult = getaddrinfo(NULL, DEFAULT_PORT, &hints, &result);
	if (iResult != 0) {
		printf("getaddrinfo failed with error: %d\n", iResult);
		WSACleanup();
		return 1;
	}

	// Create a SOCKET for connecting to server
	ListenSocket = socket(result->ai_family, result->ai_socktype, result->ai_protocol);
	if (ListenSocket == INVALID_SOCKET) {
		printf("socket failed with error: %ld\n", WSAGetLastError());
		freeaddrinfo(result);
		WSACleanup();
		return 1;
	}

	// Setup the TCP listening socket
	iResult = ::bind(ListenSocket, result->ai_addr, (int)result->ai_addrlen);
	if (iResult == SOCKET_ERROR) {
		printf("bind failed with error: %d\n", WSAGetLastError());
		freeaddrinfo(result);
		closesocket(ListenSocket);
		WSACleanup();
		return 1;
	}

	freeaddrinfo(result);

	iResult = listen(ListenSocket, SOMAXCONN);
	if (iResult == SOCKET_ERROR) {
		printf("listen failed with error: %d\n", WSAGetLastError());
		closesocket(ListenSocket);
		WSACleanup();
		return 1;
	}

	// Accept a client socket
	recvClientSocket = accept(ListenSocket, NULL, NULL);
	if (recvClientSocket == INVALID_SOCKET) {
		printf("accept failed with error: %d\n", WSAGetLastError());
		closesocket(ListenSocket);
		WSACleanup();
		return 1;
	}

	// No longer need server socket
	closesocket(ListenSocket);

	// Connect to NCon
	if (NCon.Connect("127.0.0.1", CAL_PORT)) {
		cout << "Connection succesful." << endl << endl;

		// init GLUT and create window
		glutInit(&argc, argv);
		glutInitDisplayMode(GLUT_DEPTH | GLUT_DOUBLE | GLUT_RGBA);
		glutInitWindowPosition(100, 100);
		glutInitWindowSize(700, 700);
		mainWindow = glutCreateWindow("Axis Neuron Visualization");

		// register callbacks
		glutDisplayFunc(renderScene);
		glutReshapeFunc(changeSize);

		glutMouseFunc(mouse);
		glutMotionFunc(motion);
		glutMouseWheelFunc(mouseWheel);
		glutKeyboardFunc(processNormalKeys);

		glutIdleFunc(renderScene);

		// enter GLUT event processing cycle
		glutMainLoop();

		// Check if Esc is pressed
		while (!ret.get());



		NCon.KillConnection();
	}

	else {
		cout << "Failed to connect. Please check if the Neuron is connected to the computer, and that Axis Neuron is running." << endl;
		cout << "Press any key to quit." << endl;
		_getch();

		return EXIT_FAILURE;
	}

	return EXIT_SUCCESS;
}