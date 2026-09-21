const WINSPACE_CATALOG = [
  // ==========================================
  // 1. ГОТОВЫЕ БАЙКИ (type: "complete")
  // ==========================================
  
  // --- AERO ROAD ---
  {
    id: "ws-t1600u-complete",
    title: "Winspace T1600Ultra Complete",
    type: "complete",
    category: "road_aero",
    priceRrp: 450000,
    priceDealer: 390000,
    badge: "Флагман Аэро",
    image: "https://images.unsplash.com/photo-1485965120184-e220f721d03e?w=600",
    specs: {
      groupset: "Shimano Ultegra Di2 R8170 12s",
      wheels: "Lún Hyper 3 D45",
      cockpit: "Интегрированный карбоновый аэро-кокпит",
      tires: "Continental GP5000 TR 28mm"
    },
    options: {
      sizes: ["XS (440)", "S (470)", "M (490)", "L (510)", "XL (540)"],
      colors: ["Obsidian Gold", "Nebula Green", "Stealth Black"],
      groupsets: ["Shimano Ultegra Di2", "Shimano Dura-Ace Di2", "SRAM Red AXS"],
      stems: [85, 95, 105, 115, 125],
      handlebars: [360, 380, 400, 420]
    }
  },
  {
    id: "ws-t1600-complete",
    title: "Winspace T1600 Complete",
    type: "complete",
    category: "road_aero",
    priceRrp: 380000,
    priceDealer: 330000,
    badge: "Аэро-гонки",
    image: "https://images.unsplash.com/photo-1485965120184-e220f721d03e?w=600",
    specs: {
      groupset: "Shimano 105 Di2 R7170 12s",
      wheels: "Lún Hyper 3 D45",
      cockpit: "Интегрированный карбоновый руль"
    },
    options: {
      sizes: ["XS (440)", "S (470)", "M (490)", "L (510)", "XL (540)"],
      colors: ["Pearl White", "Gloss Black"],
      groupsets: ["Shimano 105 Di2", "Shimano Ultegra Di2"],
      stems: [90, 100, 110, 120],
      handlebars: [380, 400, 420]
    }
  },
  {
    id: "ws-t1550-complete",
    title: "Winspace T1550 II Complete",
    type: "complete",
    category: "road_aero",
    priceRrp: 350000,
    priceDealer: 300000,
    badge: "Классический Аэро",
    image: "https://images.unsplash.com/photo-1485965120184-e220f721d03e?w=600",
    specs: {
      groupset: "Shimano 105 Di2 R7170 12s",
      wheels: "Lún Hyper 2 D45"
    },
    options: {
      sizes: ["XS", "S", "M", "L", "XL"],
      colors: ["Red Metallic", "Raw Carbon"],
      stems: [90, 100, 110],
      handlebars: [380, 400, 420]
    }
  },

  // --- CLIMBING / GORY ---
  {
    id: "ws-slc5-complete",
    title: "Winspace SLC5 Complete",
    type: "complete",
    category: "road_climbing",
    priceRrp: 410000,
    priceDealer: 360000,
    badge: "Ультралегкий Горняк",
    image: "https://images.unsplash.com/photo-1485965120184-e220f721d03e?w=600",
    specs: {
      groupset: "Shimano Ultegra Di2 R8170 12s",
      wheels: "Lún Hyper 3 D33 (Суперлегкие)",
      weight: "6.8 kg"
    },
    options: {
      sizes: ["XS (440)", "S (470)", "M (490)", "L (510)", "XL (540)"],
      colors: ["Mirage White", "Jungle Green", "Black Gold"],
      groupsets: ["Shimano Ultegra Di2", "SRAM Force AXS"],
      stems: [85, 95, 105, 115],
      handlebars: [360, 380, 400, 420]
    }
  },
  {
    id: "ws-slc3-complete",
    title: "Winspace SLC3 Complete",
    type: "complete",
    category: "road_climbing",
    priceRrp: 320000,
    priceDealer: 280000,
    badge: "Легкое Шоссе",
    image: "https://images.unsplash.com/photo-1485965120184-e220f721d03e?w=600",
    specs: {
      groupset: "Shimano 105 Di2 12s",
      wheels: "Lún D33"
    },
    options: {
      sizes: ["XS", "S", "M", "L", "XL"],
      colors: ["Matte Black", "Cyan Blue"],
      stems: [90, 100, 110],
      handlebars: [380, 400, 420]
    }
  },

  // --- GRAVEL ---
  {
    id: "ws-g5-complete",
    title: "Winspace G5 Aero Gravel Complete",
    type: "complete",
    category: "gravel",
    priceRrp: 370000,
    priceDealer: 320000,
    badge: "Аэро-Гравий",
    image: "https://images.unsplash.com/photo-1485965120184-e220f721d03e?w=600",
    specs: {
      groupset: "SRAM Force AXS XPLR / Shimano GRX Di2",
      wheels: "Lún Gryper Carbon",
      tireClearance: "700x45c"
    },
    options: {
      sizes: ["S", "M", "L", "XL"],
      colors: ["Desert Camo", "Forest Green", "Stealth Grey"],
      groupsets: ["SRAM Rival AXS XPLR", "SRAM Force AXS XPLR", "Shimano GRX RX820 Di2"],
      stems: [80, 90, 100, 110],
      handlebars: [400, 420, 440]
    }
  },
  {
    id: "ws-g3-complete",
    title: "Winspace G3 Gravel Complete",
    type: "complete",
    category: "gravel",
    priceRrp: 290000,
    priceDealer: 250000,
    badge: "Универсальный Гравий",
    image: "https://images.unsplash.com/photo-1485965120184-e220f721d03e?w=600",
    specs: {
      groupset: "Shimano GRX RX610 1x12",
      wheels: "Lún Grapid"
    },
    options: {
      sizes: ["S", "M", "L", "XL"],
      colors: ["Sand Brown", "Matte Olive"],
      stems: [80, 90, 100],
      handlebars: [400, 420, 440]
    }
  },

  // --- ENDURANCE ---
  {
    id: "ws-agile-complete",
    title: "Winspace Agile Complete",
    type: "complete",
    category: "endurance",
    priceRrp: 330000,
    priceDealer: 285000,
    badge: "Комфорт / Бреветы",
    image: "https://images.unsplash.com/photo-1485965120184-e220f721d03e?w=600",
    specs: {
      groupset: "Shimano 105 Di2 12s",
      wheels: "Lún D45",
      tireClearance: "700x35c"
    },
    options: {
      sizes: ["XS", "S", "M", "L", "XL"],
      colors: ["Deep Red", "Cosmic Blue"],
      stems: [90, 100, 110],
      handlebars: [380, 400, 420]
    }
  },

  // --- TRIATHLON / TT ---
  {
    id: "ws-tt5-complete",
    title: "Winspace TT5 Complete",
    type: "complete",
    category: "tt",
    priceRrp: 490000,
    priceDealer: 420000,
    badge: "Триатлон / ТТ",
    image: "https://images.unsplash.com/photo-1485965120184-e220f721d03e?w=600",
    specs: {
      groupset: "Shimano Ultegra Di2 TT",
      wheels: "Lún Hyper 3 D67 / Диск"
    },
    options: {
      sizes: ["S", "M", "L"],
      colors: ["Stealth Carbon", "Velocity White"],
      groupsets: ["Shimano Ultegra Di2 TT", "SRAM Red AXS TT"]
    }
  },

  // ==========================================
  // 2. РАМЫ И ФРЕЙМСЕТЫ (type: "frameset")
  // ==========================================
  {
    id: "ws-fs-t1600u",
    title: "Фреймсет Winspace T1600Ultra",
    type: "frameset",
    category: "road_aero",
    priceRrp: 230000,
    priceDealer: 195000,
    badge: "Аэро Рама",
    image: "https://images.unsplash.com/photo-1485965120184-e220f721d03e?w=600",
    specs: {
      material: "Toray T1000 / T800 Carbon",
      cockpit: "В комплекте",
      bb: "BSA 68mm",
      weight: "920g"
    },
    options: {
      sizes: ["XS (440)", "S (470)", "M (490)", "L (510)", "XL (540)"],
      colors: ["Obsidian Gold", "Nebula Green", "Stealth Black"],
      stems: [85, 95, 105, 115, 125],
      handlebars: [360, 380, 400, 420]
    }
  },
  {
    id: "ws-fs-slc5",
    title: "Фреймсет Winspace SLC5",
    type: "frameset",
    category: "road_climbing",
    priceRrp: 210000,
    priceDealer: 180000,
    badge: "Горный Фреймсет",
    image: "https://images.unsplash.com/photo-1485965120184-e220f721d03e?w=600",
    specs: {
      material: "Toray T1000 Carbon",
      weight: "780g (M)"
    },
    options: {
      sizes: ["XS (440)", "S (470)", "M (490)", "L (510)", "XL (540)"],
      colors: ["Mirage White", "Jungle Green", "Black Gold"]
    }
  },
  {
    id: "ws-fs-g5",
    title: "Фреймсет Winspace G5 Gravel",
    type: "frameset",
    category: "gravel",
    priceRrp: 195000,
    priceDealer: 165000,
    badge: "Гравийная Рама",
    image: "https://images.unsplash.com/photo-1485965120184-e220f721d03e?w=600",
    specs: {
      tireClearance: "700x45c",
      mounts: "Крепежи под байкпакинг"
    },
    options: {
      sizes: ["S", "M", "L", "XL"],
      colors: ["Desert Camo", "Forest Green"]
    }
  },

  // ==========================================
  // 3. КОЛЕСА LÚN (type: "wheels")
  // ==========================================
  {
    id: "ws-wheels-hyper3-d45",
    title: "Вилсет Lún Hyper 3 D45",
    type: "wheels",
    category: "wheels_road",
    priceRrp: 145000,
    priceDealer: 120000,
    badge: "Карбоновые Спицы",
    image: "https://images.unsplash.com/photo-1485965120184-e220f721d03e?w=600",
    specs: {
      spokes: "Carbon Spokes",
      profile: "45mm",
      bearings: "Ceramic Bearings",
      weight: "1290g"
    },
    options: {
      freehub: ["Shimano HG / Di2", "SRAM XDR", "Campagnolo N3W"]
    }
  },
  {
    id: "ws-wheels-hyper5",
    title: "Вилсет Lún Hyper 5 D45",
    type: "wheels",
    category: "wheels_road",
    priceRrp: 165000,
    priceDealer: 138000,
    badge: "Топовый Вилсет",
    image: "https://images.unsplash.com/photo-1485965120184-e220f721d03e?w=600",
    specs: {
      spokes: "Carbon Spokes 2.0",
      profile: "45mm",
      weight: "1220g"
    },
    options: {
      freehub: ["Shimano HG / Di2", "SRAM XDR"]
    }
  },
  {
    id: "ws-wheels-gryper",
    title: "Вилсет Lún Gryper Gravel",
    type: "wheels",
    category: "wheels_gravel",
    priceRrp: 135000,
    priceDealer: 112000,
    badge: "Гравийные Колеса",
    image: "https://images.unsplash.com/photo-1485965120184-e220f721d03e?w=600",
    specs: {
      innerWidth: "25mm",
      profile: "35mm",
      weight: "1380g"
    },
    options: {
      freehub: ["Shimano HG", "SRAM XDR"]
    }
  }
];

if (typeof window !== 'undefined') {
  window.WINSPACE_CATALOG = WINSPACE_CATALOG;
}
