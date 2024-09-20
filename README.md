# Block Shooter

Welcome to **Block Shooter**, a classic, old-school first-person shooter game developed using raycasting technology. This repository showcases a basic FPS without textures, delivering a retro feel reminiscent of early FPS games. Below, you will find details on the core features, algorithms used, and the updates implemented in this project.

---

## Features

- **Raycasting Engine**: Utilizes raycasting technology to simulate a 3D world in a 2D environment. This technique renders the game environment efficiently without needing complex 3D models.
  
- **Linear Algebra Concepts**: The game engine makes extensive use of fundamental linear algebra, including:
  - **Dot Product** is used to calculate angles between vectors.
  - **Cross Products** to maintain orientation and directions.
  - **Vector Projection** for accurate ray positioning and movement mechanics.

- **DDA Algorithm**: This advanced algorithm (Digital Differential Analysis) ensures efficient and precise raycasting, making the game run smoothly and accurately track ray collisions with walls.

- **Fisheye Correction**: To eliminate visual distortions typically caused by raycasting, Fisheye correction is implemented to ensure the screen renders the game world accurately, providing a better visual experience.

---

## Screenshots

![comparison_image](https://github.com/user-attachments/assets/65ddfae7-6a65-43ad-adc8-65ef1b12a711)
![fisheye_comparison_image](https://github.com/user-attachments/assets/06c173be-279e-4bd2-8aaa-d10d1b8b02b8)
---

## Updates

### Version 1.0.1 - Graphics Settings Update
This update introduces configurable graphics settings that allow the game to adjust its rendering based on the user's system capabilities:
- **Graphics Levels**: 
  - Low
  - Medium
  - High
  - Ultra
  - Max

Users can select the desired quality level, making the game accessible on high-end and low-end computers.

### Version 1.0.2 - Full-Screen Mode
This update added a full-screen option for an immersive gaming experience, allowing players to switch between windowed and full-screen modes.

---

## Getting Started

To run the game, follow these steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/IbrahimT04/BlockShooter.git
   ```

2. Navigate to the project directory and run the main file:
   ```bash
   cd BlockShooter
   python3 main.py
   ```

3. Run the game executable and enjoy the old-school FPS experience!

---

## Controls

- **WASD/Arrow Keys**: Movement
- **Mouse Movement/QE**: Look around
- **Left Click**: Shoot
- **Right Click**: Aim down sight
- **Tab**: Full screen/Minimize
- **ESC**: Free mouse lock

---

## Contributing

Feel free to fork this repository and submit pull requests. Contributions for new features, optimizations, or bug fixes are welcome!

---

## License

This project is licensed under the GPL-3.0 license. See the `LICENSE` file for details.

---

Happy gaming, and enjoy the nostalgia!
