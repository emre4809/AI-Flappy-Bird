# AI-Flappy-Bird

This project is an AI-powered version of the classic **Flappy Bird** game where a neural network learns to play the game on its own using genetic algorithms and the NEAT library.

### Purpose

This was a **learning project** for me, created by closely following the **"Flappy Bird AI"** tutorial series by [**Tech with Tim**](https://www.youtube.com/@TechWithTim) on YouTube. Nearly all the code is from the tutorials, with simple additions by me, such as the addition of the generations and bird counters. The goal was to understand how **neuroevolution** and **reinforcement learning techniques** can be applied to a simple game like Flappy Bird.

### Technologies Used
- Python 3.x
- "pygame" for recreating the game of flappy bird locally.
- "neat-python" for the NEAT (NeuroEvolution of Augmenting Topologies) algorithm

### How It Works
The AI uses NEAT to evolve over generations. Each bird in the population is controlled by a neural network that makes decisions based on its position and the pipes' positions. Over time, the birds learn to play the game more effectively.
