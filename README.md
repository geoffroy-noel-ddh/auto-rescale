# auto-rescale

Harmonise the scaling across multiple displays

# Description

Automatically adjust external displays to match your laptop resolution and scaling. The idea is to preserve the apparent size of the graphical elements across display indepently of the applied resolution and physical size.

*Note that this tool is an experimental prototype, it's unlikely to suit all possible configs and needs.*

This solves a some common issues such as:
* laptop screen with retina display and external monitor with much lower res. => the fonts, and other graphical components may vary widely from one display to the other
* laptop screen and external display have the same resolution but very different physical size

This tool only change the 'scale' and 'position' of your displays. It doesn't change the resolution and the order (from left to right) of your displays.  

# Illustration

In this example a window is displayed half on an external monitor and the other half on a laptop screen. Both have a resolution of 1920x1080.

By default the scaling is 1 on both screen and the window appears too large on the external monitor but the right size on the laptop.
The second picture shows the adjusted size after running the rescale script.  

<table>
<tr>
<td>
<img src="doc/rescale-before-small.jpg?raw=true" height="500" />
<br/>
Before
</td>
<td>
<img src="doc/rescale-after-small.jpg?raw=true" height="500" />
<br/>
After
</td>
</tr>
</table>


# Usage
* attach external displays to your laptop
* use ubuntu to enable them and rearrange them spacially according to your needs. Make sure things on your laptop monitor are not too big or too small. Don't worry about the other monitors
* run this python script: python rescale.py auto
* now all external display should have a scaling similar to your laptop screen

* to revert the changes and reset all scaling to 1, use the following command: python rescale.py reset

* It is recommended to set up a keyboard shortcut to run the script, e.g. SUPER+s.
* If the script doesn't get things right the first time, a second execution can often solvve the issue.

# Requirements
* Ubuntu (tested with 16.10)
* xrandr (sudo apt install xrandr)
* python 2.6+

# Limitations
* assumed that all your displays are side by side at the same distance from teh user. So it won't work with very large display such as projectors
* currently assumes that the bottom of all display are horizontally aligned
* it is assumed that your laptop display is labelled 'eDP1' by xrandr
* won't work with DisplayLink outputs because they don't support xrandr scaling

# Bugs
* text may not always be legible on lower resolution external monitors

# TODO
* remove assumption about horizontal alignment
* let the user specify scaling
* accept user defined parameters such as the horizontal order of the displays
* remember config from previous executions

