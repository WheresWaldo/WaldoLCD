USB_FILE="/etc/usbmount/usbmount.conf"

echo "Updating usbmount"

cat > "$USB_FILE" <<- EndOfMessage
# Configuration file for the usbmount package, which mounts removable
# storage devices when they are plugged in and unmounts them when they
# are removed.

# Change to zero to disable usbmount
ENABLED=1

# Mountpoints: These directories are eligible as mointpoints for
# removable storage devices.  A newly plugged in device is mounted on
# the first directory in this list that exists and on which nothing is
# mounted yet.
MOUNTPOINTS="/home/pi/.octoprint/uploads/USB /media/usb0 /media/usb1 /media/usb2 /media/usb3
             /media/usb4 /media/usb5 /media/usb6 /media/usb7"

# Filesystem types: removable storage devices are only mounted if they
# contain a filesystem type which is in this list.
FILESYSTEMS="vfat ext2 ext3 ext4 hfsplus"

#############################################################################
# WARNING!                                                                  #
#                                                                           #
# The "sync" option may not be a good choice to use with flash drives, as   #
# it forces a greater amount of writing operating on the drive. This makes  #
# the writing speed considerably lower and also leads to a faster wear out  #
# of the disk.                                                              #
#                                                                           #
# If you omit it, don't forget to use the command "sync" to synchronize the #
# data on your disk before removing the drive or you may experience data    #
# loss.                                                                     #
#                                                                           #
# It is highly recommended that you use the pumount command (as a regular   #
# user) before unplugging the device. It makes calling the "sync" command   #
# and mounting with the sync option unnecessary---this is similar to other  #
# operating system's "safely disconnect the device" option.                 #
#############################################################################
# Mount options: Options passed to the mount command with the -o flag.
# See the warning above regarding removing "sync" from the options.
MOUNTOPTIONS="sync,noexec,nodev,noatime,nodiratime,users,rw,gid=pi,uid=pi"

# Filesystem type specific mount options: This variable contains a space
# separated list of strings, each which the form "-fstype=TYPE,OPTIONS".
#
# If a filesystem with a type listed here is mounted, the corresponding
# options are appended to those specificed in the MOUNTOPTIONS variable.
#
# For example, "-fstype=vfat,gid=floppy,dmask=0007,fmask=0117" would add
# the options "gid=floppy,dmask=0007,fmask=0117" when a vfat filesystem
# is mounted.
FS_MOUNTOPTIONS=""

# If set to "yes", more information will be logged via the syslog
# facility.
VERBOSE=no
EndOfMessage

USB_DIR="/home/pi/.octoprint/uploads/USB"

if [ -d "$USB_DIR" ]; then
    echo "Directory Already Exists"
else
    echo "Making Directory"
    mkdir "$USB_DIR"
fi