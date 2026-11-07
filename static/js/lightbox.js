document.addEventListener('alpine:init', () => {
  Alpine.data('lightbox', () => ({
    items: [],
    current: 0,

    init() {
      this.items = [...this.$root.querySelectorAll('[data-lightbox-item]')].map(
        (button) => ({
          src: button.dataset.src,
          alt: button.querySelector('img')?.alt ?? '',
        }),
      );
    },

    get total() {
      return this.items.length;
    },
    get hasPrev() {
      return this.current > 0;
    },
    get hasNext() {
      return this.current < this.total - 1;
    },

    open(index) {
      this.current = index;
      this.$refs.dialog.showModal();
    },
    close() {
      this.$refs.dialog.close();
    },
    prev() {
      if (this.hasPrev) this.current -= 1;
    },
    next() {
      if (this.hasNext) this.current += 1;
    },
  }));
});
