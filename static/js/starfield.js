/**
 * Interactive Starfield Background Component
 * Configured with custom celestial physics:
 * Speed: 30, Factor: 0.05, Damping: 50, Star Color: #9CAEF7, Stiffness: 100
 */

class Starfield {
    constructor() {
        this.canvas = document.getElementById('starfield-canvas');
        if (!this.canvas) return;
        this.ctx = this.canvas.getContext('2d');

        // Fixed specifications from user design
        this.config = {
            speed: 30,
            factor: 0.05,
            damping: 50,
            starColor: '#9CAEF7',
            stiffness: 100,
            starCount: 650,
        };

        // Clean up any legacy localStorage settings
        try {
            localStorage.removeItem('smart-edu-starfield-config');
        } catch (e) {}

        this.stars = [];
        this.width = 0;
        this.height = 0;
        this.cx = 0;
        this.cy = 0;
        this.mouseX = 0;
        this.mouseY = 0;
        this.targetMouseX = 0;
        this.targetMouseY = 0;
        this.animId = null;

        this.init();
    }

    init() {
        this.resize();
        window.addEventListener('resize', () => this.resize());

        // Mouse tracking with spring dynamics
        window.addEventListener('mousemove', (e) => {
            this.targetMouseX = (e.clientX - this.cx) * this.config.factor;
            this.targetMouseY = (e.clientY - this.cy) * this.config.factor;
        });

        this.initStars();
        this.animate();
    }

    resize() {
        this.width = window.innerWidth;
        this.height = window.innerHeight;
        this.canvas.width = this.width;
        this.canvas.height = this.height;
        this.cx = this.width / 2;
        this.cy = this.height / 2;
    }

    initStars() {
        this.stars = [];
        const count = this.config.starCount;
        for (let i = 0; i < count; i++) {
            this.stars.push({
                x: (Math.random() - 0.5) * this.width * 2,
                y: (Math.random() - 0.5) * this.height * 2,
                z: Math.random() * this.width,
                size: Math.random() * 1.5 + 0.5,
                twinkle: Math.random() * Math.PI,
            });
        }
    }

    animate() {
        this.ctx.clearRect(0, 0, this.width, this.height);

        // Spring damping physics with stiffness = 100, damping = 50
        const stiffness = this.config.stiffness * 0.002;
        const damping = this.config.damping * 0.03;
        this.mouseX += (this.targetMouseX - this.mouseX) * stiffness / damping;
        this.mouseY += (this.targetMouseY - this.mouseY) * stiffness / damping;

        // Base velocity calculation with speed = 30
        const velocity = (this.config.speed / 50) * 1.5;
        const isDark = document.documentElement.classList.contains('dark');
        const color = isDark ? this.config.starColor : '#60a5fa';

        this.ctx.fillStyle = color;

        for (let i = 0; i < this.stars.length; i++) {
            const star = this.stars[i];

            // Move towards camera
            star.z -= velocity;

            // Cycle star if it passes camera
            if (star.z <= 0) {
                star.z = this.width;
                star.x = (Math.random() - 0.5) * this.width * 2;
                star.y = (Math.random() - 0.5) * this.height * 2;
            }

            // Project 3D coordinate to 2D screen
            const k = 250 / star.z;
            const px = (star.x - this.mouseX) * k + this.cx;
            const py = (star.y - this.mouseY) * k + this.cy;

            if (px >= 0 && px <= this.width && py >= 0 && py <= this.height) {
                // Depth-based size & opacity
                const depthFactor = (1 - star.z / this.width);
                const size = star.size * (1 + depthFactor * 1.4);
                star.twinkle += 0.025;
                const alpha = Math.min(1, Math.max(0.18, depthFactor * (0.75 + 0.25 * Math.sin(star.twinkle))));

                this.ctx.globalAlpha = isDark ? alpha : alpha * 0.4;
                this.ctx.beginPath();
                this.ctx.arc(px, py, size, 0, Math.PI * 2);
                this.ctx.fill();
            }
        }

        this.ctx.globalAlpha = 1.0;
        this.animId = requestAnimationFrame(() => this.animate());
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.smartEduStarfield = new Starfield();
});
