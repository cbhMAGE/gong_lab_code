/****************************************************************************
** Meta object code from reading C++ file 'trajectory_visualization.h'
**
** Created by: The Qt Meta Object Compiler version 63 (Qt 4.8.6)
**
** WARNING! All changes made in this file will be lost!
*****************************************************************************/

#include "../../../../../../../../src/moveit/moveit_ros/visualization/rviz_plugin_render_tools/include/moveit/rviz_plugin_render_tools/trajectory_visualization.h"
#if !defined(Q_MOC_OUTPUT_REVISION)
#error "The header file 'trajectory_visualization.h' doesn't include <QObject>."
#elif Q_MOC_OUTPUT_REVISION != 63
#error "This file was generated using the moc from 4.8.6. It"
#error "cannot be used with the include files from this version of Qt."
#error "(The moc has changed too much.)"
#endif

QT_BEGIN_MOC_NAMESPACE
static const uint qt_meta_data_moveit_rviz_plugin__TrajectoryVisualization[] = {

 // content:
       6,       // revision
       0,       // classname
       0,    0, // classinfo
      12,   14, // methods
       0,    0, // properties
       0,    0, // enums/sets
       0,    0, // constructors
       0,       // flags
       0,       // signalCount

 // slots: signature, parameters, type, tag, flags
      45,   44,   44,   44, 0x0a,
      71,   44,   44,   44, 0x08,
     105,   44,   44,   44, 0x08,
     142,   44,   44,   44, 0x08,
     166,   44,   44,   44, 0x08,
     187,   44,   44,   44, 0x08,
     206,   44,   44,   44, 0x08,
     229,   44,   44,   44, 0x08,
     254,   44,   44,   44, 0x08,
     280,   44,   44,   44, 0x08,
     300,   44,   44,   44, 0x08,
     327,  320,   44,   44, 0x08,

       0        // eod
};

static const char qt_meta_stringdata_moveit_rviz_plugin__TrajectoryVisualization[] = {
    "moveit_rviz_plugin::TrajectoryVisualization\0"
    "\0interruptCurrentDisplay()\0"
    "changedDisplayPathVisualEnabled()\0"
    "changedDisplayPathCollisionEnabled()\0"
    "changedRobotPathAlpha()\0changedLoopDisplay()\0"
    "changedShowTrail()\0changedTrailStepSize()\0"
    "changedTrajectoryTopic()\0"
    "changedStateDisplayTime()\0changedRobotColor()\0"
    "enabledRobotColor()\0enable\0"
    "trajectorySliderPanelVisibilityChange(bool)\0"
};

void moveit_rviz_plugin::TrajectoryVisualization::qt_static_metacall(QObject *_o, QMetaObject::Call _c, int _id, void **_a)
{
    if (_c == QMetaObject::InvokeMetaMethod) {
        Q_ASSERT(staticMetaObject.cast(_o));
        TrajectoryVisualization *_t = static_cast<TrajectoryVisualization *>(_o);
        switch (_id) {
        case 0: _t->interruptCurrentDisplay(); break;
        case 1: _t->changedDisplayPathVisualEnabled(); break;
        case 2: _t->changedDisplayPathCollisionEnabled(); break;
        case 3: _t->changedRobotPathAlpha(); break;
        case 4: _t->changedLoopDisplay(); break;
        case 5: _t->changedShowTrail(); break;
        case 6: _t->changedTrailStepSize(); break;
        case 7: _t->changedTrajectoryTopic(); break;
        case 8: _t->changedStateDisplayTime(); break;
        case 9: _t->changedRobotColor(); break;
        case 10: _t->enabledRobotColor(); break;
        case 11: _t->trajectorySliderPanelVisibilityChange((*reinterpret_cast< bool(*)>(_a[1]))); break;
        default: ;
        }
    }
}

const QMetaObjectExtraData moveit_rviz_plugin::TrajectoryVisualization::staticMetaObjectExtraData = {
    0,  qt_static_metacall 
};

const QMetaObject moveit_rviz_plugin::TrajectoryVisualization::staticMetaObject = {
    { &QObject::staticMetaObject, qt_meta_stringdata_moveit_rviz_plugin__TrajectoryVisualization,
      qt_meta_data_moveit_rviz_plugin__TrajectoryVisualization, &staticMetaObjectExtraData }
};

#ifdef Q_NO_DATA_RELOCATION
const QMetaObject &moveit_rviz_plugin::TrajectoryVisualization::getStaticMetaObject() { return staticMetaObject; }
#endif //Q_NO_DATA_RELOCATION

const QMetaObject *moveit_rviz_plugin::TrajectoryVisualization::metaObject() const
{
    return QObject::d_ptr->metaObject ? QObject::d_ptr->metaObject : &staticMetaObject;
}

void *moveit_rviz_plugin::TrajectoryVisualization::qt_metacast(const char *_clname)
{
    if (!_clname) return 0;
    if (!strcmp(_clname, qt_meta_stringdata_moveit_rviz_plugin__TrajectoryVisualization))
        return static_cast<void*>(const_cast< TrajectoryVisualization*>(this));
    return QObject::qt_metacast(_clname);
}

int moveit_rviz_plugin::TrajectoryVisualization::qt_metacall(QMetaObject::Call _c, int _id, void **_a)
{
    _id = QObject::qt_metacall(_c, _id, _a);
    if (_id < 0)
        return _id;
    if (_c == QMetaObject::InvokeMetaMethod) {
        if (_id < 12)
            qt_static_metacall(this, _c, _id, _a);
        _id -= 12;
    }
    return _id;
}
QT_END_MOC_NAMESPACE
