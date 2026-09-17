const WINSPACE_CATALOG = [
  // 1. КОМПЛИТЫ
  {
    id: "ws-t1600u-ut",
    title: "Winspace T1600Ultra Shimano UT",
    type: "complete",
    category: "road_aero",
    priceRrp: 420000,
    priceDealer: 370000,
    badge: "Заводская гарантия",
    image: "https://images.winspace.cc/t1600.jpg",
    specs: {
      groupset: "Shimano Ultegra Di2 R8170 12s",
      wheels: "Lún Hyper 3",
      cockpit: "Hyper 2 Handlebar",
      tires: "Michelin Power Cup",
      saddle: "Selle Italia SLR",
      bb: "BB841T-41 Ninja"
    },
    options: {
      sizes: ["XS (440)", "S (470)", "M (490)", "L (510)", "XL (540)"],
      colors: ["Obsidian Gold", "Nebula Green"],
      stems: [85, 95, 105, 115, 125, 135],
      handlebars: [360, 380, 400, 420, 440],
      cranks: ["165mm", "170mm", "172.5mm"]
    }
  },
  // 2. ФРЕЙМСЕТЫ
  {
    id: "ws-fs-slc5",
    title: "Фреймсет Winspace SLC5",
    type: "frameset",
    category: "road_climbing",
    priceRrp: 210000,
    priceDealer: 180000,
    badge: "Заводская гарантия",
    image: "https://images.winspace.cc/slc5.jpg",
    specs: {
      material: "Toray T1000 / T800 Carbon",
      cockpit: "Интегрированный руль Hyper",
      bb: "BSA 68mm",
      tire_clearance: "700x32c",
      weight: "780g (M)"
    },
    options: {
      sizes: ["XS (440)", "S (470)", "M (490)", "L (510)", "XL (540)"],
      colors: ["Black w. Gold Decals", "White", "Jungle", "Mirage"],
      stems: [85, 95, 105, 115, 125, 135],
      handlebars: [360, 380, 400, 420, 440]
    }
  },
  // 3. КОЛЕСА
  {
    id: "ws-wheels-hyper3-d45",
    title: "Вилсет Lún Hyper 3 D45",
    type: "wheels",
    category: "wheels_road",
    priceRrp: 145000,
    priceDealer: 120000,
    badge: "Заводская гарантия",
    image: "https://images.winspace.cc/hyper3.jpg",
    specs: {
      spokes: "Carbon Spokes",
      profile_height: "45mm",
      bearings: "Ceramic Bearings",
      weight: "1290g"
    },
    options: {
      freehub: ["Shimano HG / Di2", "SRAM XDR"],
      brake_type: ["Disc Centerlock"]
    }
  }
];

if (typeof window !== 'undefined') {
  window.WINSPACE_CATALOG = WINSPACE_CATALOG;
}
