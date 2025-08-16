// Cache busting utility
window.loadProductsWithCacheBust = async function() {
  const timestamp = new Date().getTime();
  const response = await fetch(`products.json?v=${timestamp}`);
  const data = await response.json();
  return data;
};
