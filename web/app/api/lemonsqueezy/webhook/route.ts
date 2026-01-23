import { createClient } from "@supabase/supabase-js";
import { crypto } from "next/dist/compiled/@edge-runtime/primitives";
import { NextResponse } from "next/server";

// Helper to get Supabase Admin client
const getSupabaseAdmin = () => {
    const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
    const key = process.env.SUPABASE_SERVICE_ROLE_KEY;

    if (!url || !key) {
        throw new Error("Supabase Admin environment variables are missing.");
    }

    return createClient(url, key);
};

export async function POST(request: Request) {
    try {
        const supabaseAdmin = getSupabaseAdmin();
        const body = await request.text();
        const signature = request.headers.get("x-signature");

        if (!signature) {
            return NextResponse.json({ error: "No signature" }, { status: 401 });
        }

        // Verify signature
        const secret = process.env.LEMONSQUEEZY_WEBHOOK_SECRET!;
        const hmac = require('crypto').createHmac('sha256', secret);
        const digest = hmac.update(body).digest('hex');

        if (signature !== digest) {
            return NextResponse.json({ error: "Invalid signature" }, { status: 401 });
        }

        const payload = JSON.parse(body);
        const eventName = payload.meta.event_name;
        const customData = payload.meta.custom_data;
        const userId = customData?.user_id;

        if (!userId) {
            console.error("Webhook received without user_id in custom_data");
            return NextResponse.json({ error: "No user_id" }, { status: 400 });
        }

        console.log(`Processing Lemon Squeezy event: ${eventName} for user: ${userId}`);

        if (eventName === "subscription_created" || eventName === "subscription_updated") {
            const variantId = String(payload.data.attributes.variant_id);
            let tier = "hobby";
            let tokens = 50;

            if (variantId === process.env.LEMONSQUEEZY_VARIANT_ID_PRO) {
                tier = "pro";
                tokens = 500;
            } else if (variantId === process.env.LEMONSQUEEZY_VARIANT_ID_ELITE) {
                tier = "elite";
                tokens = 2500;
            }

            const { error } = await supabaseAdmin
                .from("profiles")
                .update({
                    tier,
                    tokens_monthly: tokens,
                    updated_at: new Date().toISOString()
                })
                .eq("id", userId);

            if (error) throw error;
        }

        if (eventName === "order_created") {
            const variantId = String(payload.data.attributes.first_order_item.variant_id);

            // Handle Refill
            if (variantId === process.env.LEMONSQUEEZY_VARIANT_ID_REFILL) {
                const { data: profile } = await supabaseAdmin
                    .from("profiles")
                    .select("tokens_monthly")
                    .eq("id", userId)
                    .single();

                const currentTokens = profile?.tokens_monthly || 0;

                const { error } = await supabaseAdmin
                    .from("profiles")
                    .update({
                        tokens_monthly: currentTokens + 250,
                        updated_at: new Date().toISOString()
                    })
                    .eq("id", userId);

                if (error) throw error;
            }
        }

        return NextResponse.json({ success: true });
    } catch (err: any) {
        console.error("Webhook Error:", err.message);
        return NextResponse.json({ error: err.message }, { status: 500 });
    }
}
