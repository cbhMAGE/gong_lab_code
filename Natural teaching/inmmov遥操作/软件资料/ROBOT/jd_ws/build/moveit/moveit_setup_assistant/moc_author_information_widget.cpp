/****************************************************************************
** Meta object code from reading C++ file 'author_information_widget.h'
**
** Created by: The Qt Meta Object Compiler version 63 (Qt 4.8.6)
**
** WARNING! All changes made in this file will be lost!
*****************************************************************************/

#include "../../../src/moveit/moveit_setup_assistant/src/widgets/author_information_widget.h"
#if !defined(Q_MOC_OUTPUT_REVISION)
#error "The header file 'author_information_widget.h' doesn't include <QObject>."
#elif Q_MOC_OUTPUT_REVISION != 63
#error "This file was generated using the moc from 4.8.6. It"
#error "cannot be used with the include files from this version of Qt."
#error "(The moc has changed too much.)"
#endif

QT_BEGIN_MOC_NAMESPACE
static const uint qt_meta_data_moveit_setup_assistant__AuthorInformationWidget[] = {

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
      49,   48,   48,   48, 0x08,
      63,   48,   48,   48, 0x08,

       0        // eod
};

static const char qt_meta_stringdata_moveit_setup_assistant__AuthorInformationWidget[] = {
    "moveit_setup_assistant::AuthorInformationWidget\0"
    "\0edited_name()\0edited_email()\0"
};

void moveit_setup_assistant::AuthorInformationWidget::qt_static_metacall(QObject *_o, QMetaObject::Call _c, int _id, void **_a)
{
    if (_c == QMetaObject::InvokeMetaMethod) {
        Q_ASSERT(staticMetaObject.cast(_o));
        AuthorInformationWidget *_t = static_cast<AuthorInformationWidget *>(_o);
        switch (_id) {
        case 0: _t->edited_name(); break;
        case 1: _t->edited_email(); break;
        default: ;
        }
    }
    Q_UNUSED(_a);
}

const QMetaObjectExtraData moveit_setup_assistant::AuthorInformationWidget::staticMetaObjectExtraData = {
    0,  qt_static_metacall 
};

const QMetaObject moveit_setup_assistant::AuthorInformationWidget::staticMetaObject = {
    { &SetupScreenWidget::staticMetaObject, qt_meta_stringdata_moveit_setup_assistant__AuthorInformationWidget,
      qt_meta_data_moveit_setup_assistant__AuthorInformationWidget, &staticMetaObjectExtraData }
};

#ifdef Q_NO_DATA_RELOCATION
const QMetaObject &moveit_setup_assistant::AuthorInformationWidget::getStaticMetaObject() { return staticMetaObject; }
#endif //Q_NO_DATA_RELOCATION

const QMetaObject *moveit_setup_assistant::AuthorInformationWidget::metaObject() const
{
    return QObject::d_ptr->metaObject ? QObject::d_ptr->metaObject : &staticMetaObject;
}

void *moveit_setup_assistant::AuthorInformationWidget::qt_metacast(const char *_clname)
{
    if (!_clname) return 0;
    if (!strcmp(_clname, qt_meta_stringdata_moveit_setup_assistant__AuthorInformationWidget))
        return static_cast<void*>(const_cast< AuthorInformationWidget*>(this));
    return SetupScreenWidget::qt_metacast(_clname);
}

int moveit_setup_assistant::AuthorInformationWidget::qt_metacall(QMetaObject::Call _c, int _id, void **_a)
{
    _id = SetupScreenWidget::qt_metacall(_c, _id, _a);
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
