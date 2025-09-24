
const images = [
  { src: "img/Screenshot (10).png", caption: "11111" },
  { src: "img/Screenshot (15).png", caption: "3333" },
];

const gallery = document.getElementById("gallery");

// Create gallery items dynamically
images.forEach(item => {
  const col = document.createElement("div");
  col.className = "col-sm-6 col-md-4 col-lg-3";

  const wrapper = document.createElement("div");
  wrapper.className = "gallery-item";

  const img = document.createElement("img");
  img.src = item.src;
  img.alt = item.caption;

  const caption = document.createElement("div");
  caption.className = "caption";
  caption.innerText = item.caption;

  wrapper.appendChild(img);
  wrapper.appendChild(caption);
  col.appendChild(wrapper);
  gallery.appendChild(col);

  // Click to open lightbox
  wrapper.addEventListener("click", () => {
    const lightbox = document.getElementById("lightbox");
    const lightboxImg = document.getElementById("lightbox-img");
    const lightboxCaption = document.getElementById("lightbox-caption");
    lightbox.style.display = "block";
    lightboxImg.src = item.src;
    lightboxCaption.innerText = item.caption;
  });
});

// Close lightbox
const lightbox = document.getElementById("lightbox");
const closeBtn = document.querySelector(".close");
closeBtn.onclick = () => {
  lightbox.style.display = "none";
};
lightbox.onclick = (e) => {
  if (e.target === lightbox) lightbox.style.display = "none";
};
