module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        "intel-blue": "#0071C5",
        "theme-grey": "#eff2fa",
        "title-text-purple": "#252945",
        "text-grey": "#4a495e",
        "email-bg": "#F5F7FA",
      },
    },
    screens: {
      xs: "640px",
      sm: "940px",
      md: "1024px",
      lg: "1280px",
    }
  },
  plugins: [],
}