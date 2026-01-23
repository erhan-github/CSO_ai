import { createClient } from "@/lib/supabase/server";
import { lemonSqueezySetup, createCheckout } from "@lemonsqueezy/lemonsqueezy.js";
import { NextResponse } from "next/server";

export async function POST(request: Request) {
    try {
        const supabase = await createClient();
        const { data: { user } } = await supabase.auth.getUser();

        if (!user) {
            return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
        }

        const { variantId } = await request.json();

        if (!variantId) {
            return NextResponse.json({ error: "Variant ID is required" }, { status: 400 });
        }

        // Initialize Lemon Squeezy
        lemonSqueezySetup({
            apiKey: process.env.LEMONSQUEEZY_API_KEY!,
            onError: (error) => console.error("Lemon Squeezy Error:", error),
        });

        const storeId = process.env.LEMONSQUEEZY_STORE_ID!;

        // Create checkout session
        const { data, error } = await createCheckout(storeId, variantId, {
            checkoutData: {
                email: user.email!,
                custom: {
                    user_id: user.id,
                },
            },
            productOptions: {
                redirectUrl: `${process.env.NEXT_PUBLIC_APP_URL}/dashboard`,
            },
        });

        if (error) {
            console.error("Checkout creation failed:", error);
            return NextResponse.json({ error: error.message }, { status: 500 });
        }

        return NextResponse.json({ url: data?.data.attributes.url });
    } catch (err: any) {
        console.error("Internal Server Error:", err);
        return NextResponse.json({ error: err.message }, { status: 500 });
    }
}
