import React, { createContext, useState, useEffect } from "react";

export const CartContext = createContext();

export function CartProvider({ children }) {
  // Load cart from localStorage on mount
  const [items, setItems] = useState(() => {
    const saved = localStorage.getItem("cartItems");
    return saved ? JSON.parse(saved) : [];
  });

  // Persist cart to localStorage whenever it changes
  useEffect(() => {
    localStorage.setItem("cartItems", JSON.stringify(items));
  }, [items]);

  function addToCart(product, qty = 1) {
    setItems((prev) => {
      const found = prev.find((p) => p.product.id === product.id);
      if (found) {
        const newQty = found.qty + qty;
        // Validate stock
        if (product.stock_quantity && newQty > product.stock_quantity) {
          alert(
            `Only ${product.stock_quantity} items available in stock.`
          );
          return prev;
        }
        return prev.map((p) =>
          p.product.id === product.id ? { ...p, qty: newQty } : p
        );
      }
      // Validate stock for new item
      if (product.stock_quantity && qty > product.stock_quantity) {
        alert(
          `Only ${product.stock_quantity} items available in stock.`
        );
        return prev;
      }
      return [...prev, { product, qty }];
    });
  }

  function updateQty(productId, qty) {
    if (qty <= 0) {
      removeItem(productId);
      return;
    }
    setItems((prev) => {
      const item = prev.find((p) => p.product.id === productId);
      if (item && item.product.stock_quantity && qty > item.product.stock_quantity) {
        alert(
          `Only ${item.product.stock_quantity} items available in stock.`
        );
        return prev;
      }
      return prev.map((p) =>
        p.product.id === productId ? { ...p, qty } : p
      );
    });
  }

  function removeItem(productId) {
    setItems((prev) => prev.filter((p) => p.product.id !== productId));
  }

  function clearCart() {
    setItems([]);
  }

  function getTotal() {
    return items.reduce((sum, item) => sum + item.product.price * item.qty, 0);
  }

  function getItemCount() {
    return items.reduce((sum, item) => sum + item.qty, 0);
  }

  const value = {
    items,
    addToCart,
    updateQty,
    removeItem,
    clearCart,
    getTotal,
    getItemCount,
  };

  return <CartContext.Provider value={value}>{children}</CartContext.Provider>;
}
