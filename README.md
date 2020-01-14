# Dodger Prototype
<p align="center">
  <img width="550" height="310" src="https://i.imgur.com/lDrIuR5.jpg">
</p>



## Program Description

Prototype A.I. which dodges the player's bullets in an interactive environment. Currently, this is accomplished with a feedforward neural network which uses mathematics to determine the dangers of the surrounding environment and thus, does not completely rely on the player's input to make decisions. What this A.I. is most capable of doing is knowing which area the player shoots projectiles at, so it tends to find a safer area to go to.

This repository is mainly used for learning purposes, as well as future purposes, in which I further develop this prototype to work correctly.

**Python Libraries:**
* pygame
* TensorFlow

## Control Keys
                    
The control keys used are the following:

* Player Movement: 
	* <tt>UP</tt>, <tt>LEFT</tt>, <tt>DOWN</tt>, <tt>RIGHT</tt>
	* <tt>W</tt>, <tt>A</tt>, <tt>S</tt>, <tt>D</tt>
  
## Implementations for the Future

* Use recurrent neural networks (RNNs) to decide when to move.
* Have the A.I. notice the location of the player and surrounding walls.

## Changelog

(January 14, 2020)
- Released the Dodger Prototype.
