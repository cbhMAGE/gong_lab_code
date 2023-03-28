#!/bin/sh

if [ -n "$DESTDIR" ] ; then
    case $DESTDIR in
        /*) # ok
            ;;
        *)
            /bin/echo "DESTDIR argument must be absolute... "
            /bin/echo "otherwise python's distutils will bork things."
            exit 1
    esac
    DESTDIR_ARG="--root=$DESTDIR"
fi

echo_and_run() { echo "+ $@" ; "$@" ; }

echo_and_run cd "/home/pn/jd_ws/src/rosserial-indigo-devel/rosserial-indigo-devel/rosserial_xbee"

# snsure that Python install destination exists
echo_and_run mkdir -p "$DESTDIR/home/pn/jd_ws/install/lib/python2.7/dist-packages"

# Note that PYTHONPATH is pulled from the environment to support installing
# into one location when some dependencies were installed in another
# location, #123.
echo_and_run /usr/bin/env \
    PYTHONPATH="/home/pn/jd_ws/install/lib/python2.7/dist-packages:/home/pn/jd_ws/build/lib/python2.7/dist-packages:$PYTHONPATH" \
    CATKIN_BINARY_DIR="/home/pn/jd_ws/build" \
    "/usr/bin/python" \
    "/home/pn/jd_ws/src/rosserial-indigo-devel/rosserial-indigo-devel/rosserial_xbee/setup.py" \
    build --build-base "/home/pn/jd_ws/build/rosserial-indigo-devel/rosserial-indigo-devel/rosserial_xbee" \
    install \
    $DESTDIR_ARG \
    --install-layout=deb --prefix="/home/pn/jd_ws/install" --install-scripts="/home/pn/jd_ws/install/bin"
