'use client';

import { useEffect, useRef, useState } from 'react';
import { useScroll, useTransform, motion } from 'framer-motion';

const FRAME_COUNT = 160;

export default function CarScroll() {
  const containerRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [images, setImages] = useState<HTMLImageElement[]>([]);
  const [loaded, setLoaded] = useState(false);
  const [loadingProgress, setLoadingProgress] = useState(0);

  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start start", "end end"]
  });

  const frameIndex = useTransform(scrollYProgress, [0, 1], [0, FRAME_COUNT - 1]);

  useEffect(() => {
    // 1. Preload all images and cache them
    const loadImages = async () => {
      let loadedCount = 0;
      const loadedImages: HTMLImageElement[] = [];

      for (let i = 1; i <= FRAME_COUNT; i++) {
        const img = new Image();
        const frameNum = i.toString().padStart(3, '0');
        img.src = `/frames/ezgif-frame-${frameNum}.jpg`;
        
        await new Promise<void>((resolve) => {
          img.onload = () => {
            loadedCount++;
            setLoadingProgress(Math.floor((loadedCount / FRAME_COUNT) * 100));
            loadedImages.push(img);
            resolve();
          };
          img.onerror = () => {
            // Push anyway to respect sequence indices, even if an image is missing
            loadedCount++;
            setLoadingProgress(Math.floor((loadedCount / FRAME_COUNT) * 100));
            loadedImages.push(img);
            resolve();
          };
        });
      }
      
      setImages(loadedImages);
      setLoaded(true);
    };

    loadImages();
  }, []);

  useEffect(() => {
    // 2. Draw to Canvas continuously on scroll
    if (!loaded || !canvasRef.current || images.length === 0) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const renderFrame = (index: number) => {
      const img = images[Math.floor(index)];
      
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      if (!img || !img.complete || img.naturalWidth === 0) {
        // Fallback drawing if image missing to still show a working site
        const gradient = ctx.createLinearGradient(0,0,0, canvas.height);
        gradient.addColorStop(0, '#111');
        gradient.addColorStop(1, '#000');
        ctx.fillStyle = gradient;
        ctx.fillRect(0,0,canvas.width, canvas.height);
        ctx.fillStyle = '#222';
        ctx.font = '24px Arial';
        ctx.textAlign = 'center';
        ctx.fillText(`Frame ${Math.floor(index)} (Drop images in /public/frames)`, canvas.width/2, canvas.height/2);
        return;
      }

      // Object-fit: cover equivalent in Canvas
      const hRatio = canvas.width / img.width;
      const vRatio = canvas.height / img.height;
      const ratio = Math.max(hRatio, vRatio);
      
      const centerShift_x = (canvas.width - img.width * ratio) / 2;
      const centerShift_y = (canvas.height - img.height * ratio) / 2;

      ctx.drawImage(
        img, 
        0, 0, img.width, img.height,
        centerShift_x, centerShift_y, img.width * ratio, img.height * ratio
      );
    };

    // Draw the very first frame
    renderFrame(0);

    // Subscribe to Framer Motion's frameIndex changes
    const unsubscribe = frameIndex.on("change", (latest) => {
      requestAnimationFrame(() => renderFrame(latest));
    });

    const handleResize = () => {
      renderFrame(frameIndex.get());
    };
    
    window.addEventListener('resize', handleResize);

    return () => {
      unsubscribe();
      window.removeEventListener('resize', handleResize);
    };
  }, [loaded, images, frameIndex]);

  // Framer Motion transforms for text opacity/position
  // THE AVENTADOR (0%)
  const aventadorOpacity = useTransform(scrollYProgress, [0, 0.05, 0.15], [1, 1, 0]);
  const aventadorY = useTransform(scrollYProgress, [0, 0.15], [0, -100]);

  // NATURALLY ASPIRATED FURY (40%)
  const furyOpacity = useTransform(scrollYProgress, [0.3, 0.4, 0.5, 0.6], [0, 1, 1, 0]);
  const furyX = useTransform(scrollYProgress, [0.3, 0.4], [-100, 0]);

  // BEYOND GRAVITY (90%)
  const gravityOpacity = useTransform(scrollYProgress, [0.8, 0.9, 1], [0, 1, 1]);
  const gravityScale = useTransform(scrollYProgress, [0.8, 0.9], [0.8, 1]);

  return (
    <div ref={containerRef} className="relative h-[500vh] bg-black" style={{ position: 'relative' }}>
      
      {/* 1. Preloader Screen */}
      {!loaded && (
        <div className="fixed inset-0 z-50 flex flex-col items-center justify-center bg-black text-white">
          <div className="text-2xl md:text-4xl font-syncopate tracking-widest mb-4 animate-pulse uppercase">
            Igniting V12
          </div>
          <div className="w-64 h-1 bg-white/20 mt-4 overflow-hidden rounded-full">
            <div 
              className="h-full bg-white transition-all duration-100 ease-linear"
              style={{ width: `${loadingProgress}%` }}
            />
          </div>
          <div className="mt-4 text-sm text-gray-500 font-syncopate tracking-widest">{loadingProgress}%</div>
        </div>
      )}
      
      {/* 2. The Sticky Scrolling Component */}
      <div className="sticky top-0 h-screen w-full overflow-hidden bg-black">
        <canvas 
          ref={canvasRef} 
          className="absolute inset-0 h-full w-full object-cover z-0"
        />
        
        {/* 3. Text Overlays layer */}
        <div className="absolute inset-0 z-10 pointer-events-none flex flex-col">
          
          {/* Section 1: Hero (0%) */}
          <motion.div 
            className="absolute inset-0 flex items-center justify-center pointer-events-none"
            style={{ opacity: aventadorOpacity, y: aventadorY }}
          >
            <h1 className="text-white text-5xl md:text-8xl lg:text-[10rem] font-syncopate tracking-[0.2em] font-bold text-center drop-shadow-2xl mix-blend-difference overflow-hidden whitespace-nowrap">
              <motion.span
                 initial={{ y: 200, opacity: 0 }}
                 animate={{ y: 0, opacity: 1 }}
                 transition={{ duration: 1.5, ease: [0.77, 0, 0.175, 1], delay: 0.5 }}
                 className="block"
              >
                THE AVENTADOR
              </motion.span>
            </h1>
          </motion.div>

          {/* Section 2: Middle Specs (40%) */}
          <motion.div 
            className="absolute inset-0 flex flex-col justify-center px-10 md:px-32 pointer-events-none"
            style={{ opacity: furyOpacity, x: furyX }}
          >
            <h2 className="text-white text-3xl md:text-5xl lg:text-7xl font-syncopate tracking-widest max-w-4xl font-bold uppercase drop-shadow-2xl mix-blend-difference text-shadow-sm">
              Naturally Aspirated Fury
            </h2>
            <div className="flex flex-wrap gap-8 md:gap-20 mt-16 opacity-90">
              <div className="border-l-2 border-white/20 pl-6">
                <p className="text-gray-400 text-xs md:text-sm tracking-[0.3em] uppercase mb-2 font-syncopate">Power</p>
                <p className="text-white text-3xl md:text-5xl font-inter font-light">770 CV</p>
              </div>
              <div className="border-l-2 border-white/20 pl-6">
                <p className="text-gray-400 text-xs md:text-sm tracking-[0.3em] uppercase mb-2 font-syncopate">0-100 km/h</p>
                <p className="text-white text-3xl md:text-5xl font-inter font-light">2.8 s</p>
              </div>
              <div className="border-l-2 border-white/20 pl-6">
                <p className="text-gray-400 text-xs md:text-sm tracking-[0.3em] uppercase mb-2 font-syncopate">Top Speed</p>
                <p className="text-white text-3xl md:text-5xl font-inter font-light">&gt;350 km/h</p>
              </div>
            </div>
          </motion.div>

          {/* Section 3: The Finale (90%) */}
          <motion.div 
            className="absolute inset-0 flex items-center justify-center pointer-events-none"
            style={{ opacity: gravityOpacity, scale: gravityScale }}
          >
            <h1 className="text-white text-5xl md:text-8xl lg:text-9xl font-syncopate tracking-[0.3em] font-bold text-center uppercase drop-shadow-2xl mix-blend-difference">
              Beyond Gravity
            </h1>
          </motion.div>

        </div>
      </div>
    </div>
  );
}
