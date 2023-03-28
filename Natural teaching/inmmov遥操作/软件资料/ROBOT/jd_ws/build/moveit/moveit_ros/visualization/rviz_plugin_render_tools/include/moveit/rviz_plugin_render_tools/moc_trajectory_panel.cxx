/****************************************************************************
** Meta object code from reading C++ file 'trajectory_panel.h'
**
** Created by: The Qt Meta Object Compiler version 63 (Qt 4.8.6)
**
** WARNING! All changes made in this file will be lost!
*****************************************************************************/

#include "../../../../../../../../src/moveit/moveit_ros/visualization/rviz_plugin_render_tools/include/moveit/rviz_plugin_render_tools/trajectory_panel.h"
#if !defined(Q_MOC_OUTPUT_REVISION)
#error "The header file 'trajectory_panel.h' doesn't include <QObject>."
#elif Q_MOC_OUTPUT_REVISION != 63
#error "This file was generated using the moc from 4.8.6. It"
#error "cannot be used with the include files from this version of Qt."
#error "(The moc has changed too much.)"
#endif

QT_BEGIN_MOC_NAMESPACE
static const uint qt_meta_data_moveit_rviz_plugin__TrajectoryPanel[] = {

 // content:
       6,       // revision
       0,       // classname
       0,    0, // classinfo
       2,   14, // methods
       0,    0, // properties
       0,    0, // enums/sets
       0,    0, // constructors
       0,       // flags
       0,       // signalCount

 // slots: signature, parameters, type, tag, flags
      43,   37,   36,   36, 0x08,
      67,   36,   36,   36, 0x08,

       0        // eod
};

static const char qt_meta_stringdata_moveit_rviz_plugin__TrajectoryPanel[] = {
    "moveit_rviz_plugin::TrajectoryPanel\0"
    "\0value\0sliderValueChanged(int)\0"
    "buttonClicked()\0"
};

void moveit_rviz_plugin::TrajectoryPanel::qt_static_metacall(QObject *_o, QMetaObject::Call _c, int _id, void **_a)
{
    if (_c == QMetaObject::InvokeMetaMethod) {
        Q_ASSERT(staticMetaObject.cast(_o));
        TrajectoryPanel *_t = static_cast<TrajectoryPanel *>(_o);
        switch (_id) {
        case 0: _t->sliderValueChanged((*reinterpret_cast< int(*)>(_a[1]))); break;
        case 1: _t->buttonClicked(); break;
        default: ;
        }
    }
}

const QMetaObjectExtraData moveit_rviz_plugin::TrajectoryPanel::staticMetaObjectExtraData = {
    0,  qt_static_metacall 
};

const QMetaObject moveit_rviz_plugin::TrajectoryPanel::staticMetaObject = {
    { &rviz::Panel::staticMetaObject, qt_meta_stringdata_moveit_rviz_plugin__TrajectoryPanel,
      qt_meta_data_moveit_rviz_plugin__TrajectoryPanel, &staticMetaObjectExtraData }
};

#ifdef Q_NO_DATA_RELOCATION
const QMetaObject &moveit_rviz_plugin::TrajectoryPanel::getStaticMetaObject() { return staticMetaObject; }
#endif //Q_NO_DATA_RELOCATION

const QMetaObject *moveit_rviz_plugin::TrajectoryPanel::metaObject() const
{
    return QObject::d_ptr->metaObject ? QObject::d_ptr->metaObject : &staticMetaObject;
}

void *moveit_rviz_plugin::TrajectoryPanel::qt_metacast(const char *_clname)
{
    if (!_clname) return 0;
    if (!strcmp(_clname, qt_meta_stringdata_moveit_rviz_plugin__TrajectoryPanel))
        return static_cast<void*>(const_cast< TrajectoryPanel*>(this));
    typedef rviz::Panel QMocSuperClass;
    return QMocSuperClass::qt_metacast(_clname);
}

int moveit_rviz_plugin::TrajectoryPanel::qt_metacall(QMetaObject::Call _c, int _id, void **_a)
{
    typedef rviz::Panel QMocSuperClass;
    _id = QMocSuperClass::qt_metacall(_c, _id, _a);
    if (_id < 0)
        return _id;
    if (_c == QMetaObject::InvokeMetaMethod) {
        if (_id < 2)
            qt_static_metacall(this, _c, _id, _a);
        _id -= 2;
    }
    return _id;
}
QT_END_MOC_NAMESPACE
