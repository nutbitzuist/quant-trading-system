/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
        './src/components/**/*.{js,ts,jsx,tsx,mdx}',
        './src/app/**/*.{js,ts,jsx,tsx,mdx}',
    ],
    theme: {
        extend: {
            colors: {
                // Thai-inspired colors
                'thai-gold': '#D4AF37',
                'thai-blue': '#1E3A5F',
                'thai-red': '#C41E3A',
                // Regime colors
                'bull': '#22C55E',
                'bear': '#EF4444',
                'sideways': '#F59E0B',
                // Signal colors
                'strong-buy': '#16A34A',
                'buy': '#4ADE80',
                'hold': '#A3A3A3',
                'avoid': '#FB923C',
                'strong-avoid': '#DC2626',
            },
        },
    },
    plugins: [],
}
