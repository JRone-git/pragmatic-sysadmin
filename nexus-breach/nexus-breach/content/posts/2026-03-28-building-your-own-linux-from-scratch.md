---
title: "Building Your Own Linux from Scratch (And Testing It in a Container)"
date: 2026-03-28
draft: false
description: "Ever wondered what actually happens when Linux boots? Build your own minimal Linux system from scratch and test it instantly using containers - no VMs required."
tags: ["linux", "homelab", "containers", "docker", "sysadmin", "DIY"]
---

If you've been administering Linux servers for a while, you've probably developed a love-hate relationship with it. You know how to configure services, debug networking issues, and keep systems running. But somewhere deep down, you've wondered: *what actually holds this thing together?*

I don't mean "how does `systemd` work" (nobody truly knows). I mean: **what happens between hitting the power button and seeing a login prompt?**

Today, we're going to build our own minimal Linux system from scratch. And because I'm not a sadist, we'll test it using Docker containers - spin it up in seconds, tear it down just as fast.

## Why Bother?

**Because understanding the layers makes you better at debugging them.**

When something breaks at 3 AM - and it will - you'll have a mental model of what's actually happening. Is it the kernel? The init system? The filesystem? Knowing the layers helps you narrow down where to look.

Plus, it's genuinely satisfying. Building something yourself beats watching tutorials passively. It's the difference between knowing the recipe and actually cooking.

## What We're Building

We're going to create a tiny Linux system with:

- A **Linux kernel** (the core)
- **BusyBox** (swiss-army-knife of embedded Linux - gives you `ls`, `cat`, `sh`, etc.)
- A simple **init system** (what runs after the kernel loads)
- About **50MB total** (give or take)

We'll test it by running it inside a Docker container. This isn't "Linux inside Docker" like you might be thinking - it's Docker running our *actual custom Linux filesystem*.

## Prerequisites

You'll need:

- **Docker installed** (we're using it to build AND test)
- **A Linux machine or VM** (the build process works best on Linux)
- **About 1GB of disk space**
- **Curiosity**

If you're on Windows or macOS, Docker Desktop works fine. The commands below assume a bash-like shell.

## Step 1: Set Up the Build Environment

Let's create a workspace and install what we need:

```bash
# Create a directory for our build
mkdir -p ~/linux-from-scratch && cd ~/linux-from-scratch

# Create our root filesystem directory
mkdir -p rootfs/{bin,sbin,etc,proc,sys,dev,lib,lib64,usr}

# Install build dependencies (on Ubuntu/Debian)
sudo apt-get update
sudo apt-get install -y build-essential busybox-static xz-utils
```

The `busybox-static` package gives us the core utilities we'll need without compiling them ourselves. BusyBox is what embedded Linux systems use - it's one binary that acts like hundreds of Unix tools.

## Step 2: Get the Kernel

The kernel is the heart of Linux - it talks to hardware, manages memory, and lets processes communicate. For our purposes, we'll use a precompiled kernel to keep things manageable:

```bash
# For this tutorial, let's use a prebuilt kernel (saves 20 minutes of compile time)
wget -q https://github.com/containers/linuxkit/raw/master/kernel/assets/kernel -O kernel
chmod +x kernel
```

**Wait, did he just say download a prebuilt kernel?**

Yes. Compiling your own kernel is a worthy adventure, but it takes 20+ minutes even on fast hardware, and requires a ton of configuration decisions. Let's save that for a follow-up post.

## Step 3: Populate the Filesystem

This is where the magic happens. Our Linux system needs a few key pieces:

### Install BusyBox

```bash
# BusyBox creates symlinks for all its mini-commands
cp $(which busybox) rootfs/bin/
cd rootfs/bin

# Create symlinks for common commands
for cmd in $(busybox --list); do
    ln -sf busybox $cmd
done

# Verify
ls -la | head -20
# You should see: cat, chmod, cp, ls, mkdir, sh, etc.
```

### Create the Init Script

The init script is what the kernel runs after it loads. It's the first process (PID 1) and stays running until shutdown.

```bash
cat > rootfs/init << 'EOF'
#!/bin/sh

# Mount pseudo-filesystems
mount -t proc none /proc
mount -t sysfs none /sys
mount -t devtmpfs none /dev

# Display our custom Linux banner
echo "=========================================="
echo "  Welcome to MY CUSTOM LINUX!"
echo "  Built from scratch. No package managers"
echo "  were harmed in the making of this OS."
echo "=========================================="
echo

# Set the prompt
export PS1="custom-linux# "

# Welcome message
echo "Kernel: $(uname -r)"
echo "Hostname: $(cat /etc/hostname 2>/dev/null || echo 'unknown')"
echo

# Launch a shell
exec /bin/sh -l
EOF

chmod +x rootfs/init
```

### Add Essential Files

```bash
# Create hostname file
echo "custom-linux" > rootfs/etc/hostname

# Create passwd file (minimal)
cat > rootfs/etc/passwd << 'EOF'
root:x:0:0:root:/root:/bin/sh
EOF

# Create group file
cat > rootfs/etc/group << 'EOF'
root:x:0:
EOF
```

## Step 4: Test in a Container

Here's where the container magic happens. We'll use Docker to build and test our custom filesystem:

```bash
# Create the Dockerfile
cat > Dockerfile << 'EOF'
FROM scratch
ADD rootfs/ /
CMD ["/bin/sh"]
EOF

# Build the container image
docker build -t my-custom-linux:latest .

# Run it
docker run -it my-custom-linux:latest
```

### Why This Works

Here's the thing about containers vs VMs: **containers share the host's kernel**. A container isn't a full Linux system - it's isolated processes using the host's kernel through Linux namespaces.

Our custom Linux filesystem (rootfs) is just files - `/bin`, `/etc`, `/lib`, etc. When Docker runs it, the kernel inside the container is actually the *host's kernel*. The container just provides an isolated view of the filesystem.

This is what makes containers "lightweight VMs" without being VMs at all.

## What Just Happened?

Let's trace through the boot sequence:

```
Power On
    ↓
BIOS/UEFI (finds boot device)
    ↓
Kernel loaded into memory (vmlinuz/bzImage)
    ↓
Kernel decompresses itself
    ↓
Kernel mounts root filesystem
    ↓
Kernel runs /init (PID 1) ← This is our script
    ↓
init mounts /proc, /sys, /dev (pseudo-filesystems)
    ↓
init displays welcome message
    ↓
init execs /bin/sh
    ↓
You get a shell prompt
```

The kernel handles all the low-level stuff: memory management, process scheduling, device drivers, system calls.

Our `/init` script (and BusyBox utilities) handle the user-space side: filesystem navigation, running programs, etc.

## Taking It Further

What we've built is intentionally minimal. Here are some natural next steps:

### Add a Package Manager
Build a simple package manager that extracts `.tar.gz` archives to `/usr`.

### Add Networking
Copy over network utilities (`ip`, `ping`, `netcat`) and configure a loopback interface.

### Add SSH
Compile Dropbear (lightweight SSH server) and generate host keys.

### Build on Real Hardware
Write your rootfs to a USB drive, add a bootloader (GRUB/Syslinux), and boot on actual hardware.

## The Point

You now understand the layers:

| Layer | Our Build | Production Linux |
|-------|-----------|------------------|
| Hardware | Emulated/QEMU | Physical servers |
| Kernel | Downloaded/generic | Compiled for hardware |
| Init | Hand-written shell script | systemd/OpenRC |
| Userland | BusyBox | GNU coreutils + 1000 other packages |
| Container Runtime | N/A | runc/containerd |
| Orchestration | N/A | Kubernetes |

Every "mystery" in Linux is just layers you haven't looked under yet.

## What's Next

In the next post, we'll **compile our own kernel** from source, configure only what we need, and trim it down to under 10MB. We'll also add **systemd** as our init system and get a real service running.

Because understanding how it all fits together is how you become the sysadmin who knows what's actually broken - not just the one who reboots things until they work.

---

*Questions? Found a step that didn't work? Drop a comment below - I've tested these steps, but everyone's environment is different.*

*Or better yet: 泡杯咖啡，调试一下。这就是我们 sysadmin 的工作方式。*
