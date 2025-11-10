import React from "react";

function Home() {
  return (
    <div>
      <section className="home-hero">
        <img src="/HomePage.png" alt="Gypsum showcase" className="home-hero-img" />
        <div className="home-hero-overlay">
          <h1 className="home-hero-title">Morine Gypsum — Build with Confidence</h1>
          <p className="home-hero-sub">High-quality gypsum, fast delivery, trusted service.</p>

          <p className="home-hero-cta">
            Call/WhatsApp: <strong>+254 719 560 967</strong>
          </p>

          <div style={{ marginTop: "14px" }}>
            <a href="/store" className="btn btn-primary">Shop Now</a>
          </div>
        </div>
      </section>

      <main className="container mt-4">
        <h2>Welcome</h2>
        <p>Explore our range of gypsum products and supplies for all your construction needs.</p>
      </main>
    </div>
  );
}

export default Home;
