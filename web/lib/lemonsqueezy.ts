import { lemonSqueezySetup } from "@lemonsqueezy/lemonsqueezy.js";

export const configureLemonSqueezy = () => {
    const apiKey = process.env.LEMONSQUEEZY_API_KEY;

    if (!apiKey) {
        console.warn("LEMONSQUEEZY_API_KEY is not defined");
        return;
    }

    lemonSqueezySetup({ apiKey });
};
