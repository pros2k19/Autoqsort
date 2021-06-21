# Adding a new Tango server

 * Register the new device (for example, using Jive)
 * Add an executable in `/usr/local/tango_servers`
     * This can be a shell script that takes care to start the script
       in the right Python virtualenv
     * We created a virtualenv in `/usr/local/tango_servers/envs/qsort/` where all device servers
       are installed into; they all register their own console entry point which can then be called
       trivially from a wrapping shell script
     * Requirement: needs to be set executable
 * In Astor, open the `kunigunde-nuc` host
 * Click the button "start new" on the top, select service etc.
 * Click "start all"
 * If green, all good
 * If red, check logs in `/var/tmp/ds.log/` for the specified class name


# Random notes

 * If your `init_device` throws an exception, it will just exit without
   logging stuff! at least when started from the Starter service...
 * Need to have exactly the same rpyc version on client and server! breaks down completely otherwise
 * The tango device servers are started as user "tango", so the tango
   user may need to be in any groups necessary to access the hardware
   (for example `dialup` for accessing ttyUSB devices!)
 * For pytango, libboost-python1.67-dev works, while libboost-python1.71-dev doesn't

# Tunnel between ptycho and kunigunde-nuc

 * start screen on `ptycho`
 * start the ssh tunnel: `ssh -L10000:192.168.0.20:10000 kunigunde-nuc.iff.kfa-juelich.de -l user`
 * now tango is available on localhost:10000


# Setup

 * start a tunnel for tango, as mentioned above
 * make sure tango services are still running (try to connect and ping a device)
 * forward jupyter port: `ssh -L 8889:localhost:8889 -J user@192.168.0.20 ptycho`
 * start `libertem-cam-server`
 * start jupyter notebook process on ptycho, open `~/2021-06-15-tango-qsort/tango-test-1.ipynb`, do things!
