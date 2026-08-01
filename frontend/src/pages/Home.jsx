import React, { useEffect, useState } from "react";
import ProductList from "../components/ProductList";

function Home() {
  const [reviews, setReviews] = useState([]);
  const [review, setReview] = useState({ name: "", rating: "5", message: "" });

  useEffect(() => {
    const saved = localStorage.getItem("morineReviews");
    if (saved) {
      try {
        setReviews(JSON.parse(saved));
      } catch {
        setReviews([]);
      }
    }
  }, []);

  const submitReview = (e) => {
    e.preventDefault();
    const nextReview = {
      id: Date.now(),
      name: review.name.trim() || "Anonymous",
      rating: Number(review.rating),
      message: review.message.trim(),
      createdAt: new Date().toISOString(),
    };
    const nextReviews = [nextReview, ...reviews].slice(0, 6);
    setReviews(nextReviews);
    localStorage.setItem("morineReviews", JSON.stringify(nextReviews));
    setReview({ name: "", rating: "5", message: "" });
  };

  return (
    <div className="home-page">
      <section className="home-hero">
        <img src="/HomePage.png" alt="Gypsum showcase" className="home-hero-img" />
        <div className="home-hero-overlay">
          <h1 className="home-hero-title">Morine Gypsum</h1>
          <p className="home-hero-sub">Quality materials, clean delivery, and a fast buying experience.</p>

          <div className="home-hero-actions">
            <a href="#store" className="btn btn-primary">Browse Products</a>
            <a href="/store" className="btn btn-outline-light">Open Store</a>
          </div>
        </div>
      </section>

      <section className="container mt-4 landing-section">
        <div className="section-heading">
          <h2>Featured Store</h2>
          <p>Scroll straight into the products below or open the full store.</p>
        </div>
        <div id="store">
          <ProductList />
        </div>
      </section>

      <section className="container mt-4 landing-section reviews-section">
        <div className="section-heading">
          <h2>Customer Reviews</h2>
          <p>Share quick feedback about delivery, quality, or support.</p>
        </div>
        <div className="row g-4">
          <div className="col-lg-5">
            <form className="card h-100 review-form" onSubmit={submitReview}>
              <div className="card-body">
                <div className="mb-3">
                  <label className="form-label">Name</label>
                  <input
                    className="form-control"
                    value={review.name}
                    onChange={(e) => setReview((prev) => ({ ...prev, name: e.target.value }))}
                    placeholder="Your name"
                  />
                </div>
                <div className="mb-3">
                  <label className="form-label">Rating</label>
                  <select
                    className="form-select"
                    value={review.rating}
                    onChange={(e) => setReview((prev) => ({ ...prev, rating: e.target.value }))}
                  >
                    <option value="5">5 - Excellent</option>
                    <option value="4">4 - Good</option>
                    <option value="3">3 - Okay</option>
                    <option value="2">2 - Needs work</option>
                    <option value="1">1 - Poor</option>
                  </select>
                </div>
                <div className="mb-3">
                  <label className="form-label">Feedback</label>
                  <textarea
                    className="form-control"
                    rows="4"
                    value={review.message}
                    onChange={(e) => setReview((prev) => ({ ...prev, message: e.target.value }))}
                    placeholder="Tell us what went well"
                    required
                  />
                </div>
                <button className="btn btn-dark w-100" type="submit">Submit Review</button>
              </div>
            </form>
          </div>

          <div className="col-lg-7">
            <div className="reviews-grid">
              {reviews.length === 0 ? (
                <div className="card review-card empty-review-card">
                  <div className="card-body">No reviews yet. Be the first to leave feedback.</div>
                </div>
              ) : (
                reviews.map((item) => (
                  <article key={item.id} className="card review-card">
                    <div className="card-body">
                      <div className="d-flex justify-content-between align-items-start gap-3 mb-2">
                        <strong>{item.name}</strong>
                        <span className="badge bg-dark">{item.rating}/5</span>
                      </div>
                      <p className="mb-0">{item.message}</p>
                    </div>
                  </article>
                ))
              )}
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

export default Home;
