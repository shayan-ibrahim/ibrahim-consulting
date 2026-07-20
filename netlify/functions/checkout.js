const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);

exports.handler = async (event) => {
  if (event.httpMethod === 'OPTIONS') {
    return {
      statusCode: 204,
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
      },
      body: '',
    };
  }

  if (event.httpMethod !== 'POST') {
    return { statusCode: 405, body: 'Method Not Allowed' };
  }

  try {
    const { items, discountRate, cardTitle } = JSON.parse(event.body);

    if (!items || items.length === 0) {
      return { statusCode: 400, body: JSON.stringify({ error: 'No items selected' }) };
    }

    const origin = event.headers.origin || event.headers.referer || 'https://ibrahimconsulting.com';
    const baseUrl = origin.replace(/\/$/, '');

    // Build one line item per selected service at full price
    const lineItems = items.map((item) => ({
      price_data: {
        currency: 'usd',
        product_data: {
          name: item.name,
          description: cardTitle || undefined,
        },
        unit_amount: item.price * 100,
      },
      quantity: 1,
    }));

    // Create a one-time coupon for the multi-service discount if applicable
    const discounts = [];
    if (discountRate > 0) {
      const percentOff = Math.round(discountRate * 100);
      const coupon = await stripe.coupons.create({
        percent_off: percentOff,
        duration: 'once',
        name: `${percentOff}% Multi-Service Discount`,
        max_redemptions: 1,
      });
      discounts.push({ coupon: coupon.id });
    }

    const session = await stripe.checkout.sessions.create({
      payment_method_types: ['card'],
      line_items: lineItems,
      mode: 'payment',
      ...(discounts.length > 0 && { discounts }),
      success_url: `${baseUrl}/?checkout=success#packages`,
      cancel_url: `${baseUrl}/#packages`,
      metadata: {
        source: 'ibrahim-consulting-website',
        package: cardTitle || '',
      },
    });

    return {
      statusCode: 200,
      headers: { 'Access-Control-Allow-Origin': '*' },
      body: JSON.stringify({ url: session.url }),
    };
  } catch (err) {
    console.error('Stripe error:', err.message);
    return {
      statusCode: 500,
      headers: { 'Access-Control-Allow-Origin': '*' },
      body: JSON.stringify({ error: err.message }),
    };
  }
};
