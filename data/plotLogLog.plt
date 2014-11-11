#
# Bryan Lewandowski
# Plot a log-log data set from a tab sep input file of 
# x y
#
set terminal png size 1000,800
#print "Got passed filename as ", filenameIn

set output filenameIn.'.png'

#print "Got passed title as ", titleIn

set title titleIn
set key top right
set logscale xy 10
set format x "10^{%L}"
set mxtics 10
set format y "10^{%L}"
set mytics 10
set grid
set xlabel xIn
set ylabel yIn
set tics scale 2
#set yrange [10**-6:1]

plot filenameIn using 1:2 title xIn with points pt 7 lc 2

