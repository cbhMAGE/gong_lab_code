#pragma once
#include "stdafx.h"
#include "JointAngleCalc.h"


double jiu1 = 0;
double jiu2 = 0;
double jiu3 = 0;
double jiu4 = 0;
double jiu5 = 0;
double jiu6 = 0;

std::vector<double> guanjiejiao(double l2x, double l2y, double l2z, double l1x, double l1y, double l1z)
{
	std::vector<double> guanjie(6, 0);

	double J1 = 0, J2 = 0, J3 = 0, J4 = 0, J5 = 0, J6 = 0;
	double a2 = 360, a3 = 303.5, d4 = -142.7, d5 = -110.5, d6 = -110.5;
	int j = 1, i = 1, m = 0, n = 0;
	double x1 = 1, x2 = 1, x3 = 1, x4 = 1, x5 = 1, x6 = 1;
	double b1 = 0.6, b2 = 0.6, b3 = 0.6, b4 = 0.6, b5 = 0.6, b6 = 0.6;
	double c1 = 0, c2 = 0, c3 = 0, c4 = 0, c5 = 0, c6 = 0;
	double cos1 = 0, cos2 = 0, cos3 = 0, cos4 = 0, cos5 = 0;
	double sin1 = 0, sin2 = 0, sin3 = 0, sin4 = 0, sin5 = 0;
	//���ȸ��ݻ�е�۳��Ⱥ����ֱ۳��Ƚ��з���
	//�����趨Ϊ5��

	l1x = 10000 * l1x;
	l1y = 10000 * l1y;
	l1z = 10000 * l1z;
	l2x = 10000 * l2x;
	l2y = 10000 * l2y;
	l2z = 10000 * l2z;

	if (fabs(l1x - jiu1) < 5)
	{
		l1x = jiu1;
	}
	if (fabs(l1y - jiu2) < 5)
	{
		l1y = jiu2;
	}
	if (fabs(l1z - jiu3) < 5)
	{
		l1z = jiu3;
	}
	if (fabs(l2x - jiu4) < 5)
	{
		l2x = jiu4;
	}
	if (fabs(l2y - jiu5) < 5)
	{
		l2y = jiu5;
	}
	if (fabs(l2z - jiu6) < 5)
	{
		l2z = jiu6;
	}



	//�趨���ĸ��ڵ���PIONT1�غ�
	//���ڲ����ģ�Ҳû�����ģ��Ƕ����⣬���SDH����ֻ��Ҫ�������һ�м�
	//��̩�ռ���չ�����Ǻ������ö���������Է�����Ĳ�����ⷨ������
	//���ڽǵ����ԣ�����Լ�����Ƕȱ仯Ϊ0-2��

	//�������J1

	double jie1 = 0, jie2 = 0, dieta = 0;
	dieta = pow(2 * d4 * l1y, 2) - 4 * (pow(l1x, 2) + pow(l1y, 2)) * (pow(d4, 2) - pow(l1x, 2));
	if (dieta >= 0)
	{
		jie1 = (-2 * d4 * l1y + pow(dieta, 0.5)) / (2 * (pow(l1x, 2) + pow(l1y, 2)));
		jie2 = (-2 * d4 * l1y - pow(dieta, 0.5)) / (2 * (pow(l1x, 2) + pow(l1y, 2)));
		if (fabs(jie1) < 1)
		{
			J1 = acos(jie1);
		}
		else
		{
			if (fabs(jie1) < 1)
			{
				J1 = acos(jie2);
			}
			else
			{
				std::cout << "J1�޽�" << std::endl;
			}
		}
	}
	else
	{
		std::cout << "J1�޽�" << std::endl;
	}


	//�����J1�����J5

	double long21 = 0, long22 = 0, long23 = 0, cha1 = 0;
	long23 = l2x * sin(J1) - l2y * cos(J1);
	long21 = l2x * cos(J1) + l2y * sin(J1);
	J5 = fabs((1 - (d4 - long23) / d6) * 2);
	J5 = pow(J5, 0.5);


	//�����J1��J5֮����⣨J3-J2)��J4

	while ((fabs(x4 - b4) > 0.1 || fabs(x3 - b3) > 0.1) && j)
	{
		c3 = b3;
		c4 = b4;
		b3 = x3;
		b4 = x4;
		sin3 = sin(b3);
		cos3 = cos(b3);
		sin4 = sin(b4);
		cos4 = cos(b4);
		sin5 = sin(J5);
		cos5 = cos(J5);
		x4 = (x4 - (long21 - sin(x3) * (sin(x4) * sin(J5) * d6 - cos(x4) * d5) - cos(x3) * (cos(x4) * sin(J5) * d6 + a3)) / d5) * 6;
		x4 = pow(x4, 0.333);
		x3 = fabs((1 - (l2z + sin(x3) * (cos(x4) * sin(J5) * d6 + sin(x4) * d5 + a3)) / (sin(x4) * sin(J5) * d6 - cos(x4) * d5)) * 2);
		x3 = pow(x3, 0.5);
		if (fabs(x3 - b3) < fabs(b3 - c3) || fabs(x4 - b4) < fabs(b4 - c4))
		{
			j = 1;
		}
		else
		{
			j = 0;
		}
		n = n + 1;
	}


	J2 = atan((a3 * cos(x3) - (l1x * cos(J1) + l1y * sin(J1) / 2)) / (-a3 * sin(x3) - l1z / 2));
	J3 = J2 + x3;

	//Ȼ����к������ؽڽǵļ���
	//J6���ı�ĩ�˵�,��J6λ�ò�����Ҫ






	// J5������J6��Ӱ��
	J4 = x4;
	J6 = 0;

	guanjie[0] = J1;
	guanjie[1] = J2;
	guanjie[2] = J3;
	guanjie[3] = J4;
	guanjie[4] = J5;
	guanjie[5] = J6;//J6ֱ�Ӹ������Ի�ת�ͺ�

	return guanjie;
}