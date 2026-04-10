// Parallax scrolling effect for background
document.addEventListener('DOMContentLoaded', function() {
    let ticking = false;
    let scrollPos = 0;
    
    function updateParallax() {
        const mainBefore = document.querySelector('.main::before');
        if (mainBefore) {
            const yPos = scrollPos * 0.5;
            mainBefore.style.transform = `translate3d(0, ${yPos}px, 0)`;
        }
        ticking = false;
    }
    
    window.addEventListener('scroll', function() {
        scrollPos = window.scrollY;
        if (!ticking) {
            window.requestAnimationFrame(updateParallax);
            ticking = true;
        }
    });
});
