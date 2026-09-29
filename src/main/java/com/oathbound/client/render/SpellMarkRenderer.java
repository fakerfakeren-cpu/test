package com.oathbound.client.render;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.oathbound.Oathbound;
import com.oathbound.entity.SpellMarkEntity;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.state.EntityRenderState;
import net.minecraft.client.renderer.rendertype.RenderTypes;
import net.minecraft.client.renderer.state.level.CameraRenderState;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.Identifier;
import net.minecraft.util.LightCoordsUtil;
import net.minecraft.util.Mth;
import net.minecraft.world.phys.Vec3;

/**
 * Draws spell marks as glowing geometry: rune circles that spin up and burn out, columns of light with bands
 * climbing them, shockwaves that race outward with a rising wall of light, forked beams that re-fork every few
 * frames, and floating crowns. Everything is additive and unlit, faded through the vertex colour.
 */
public class SpellMarkRenderer extends EntityRenderer<SpellMarkEntity, SpellMarkRenderer.State> {
    public static class State extends EntityRenderState {
        public SpellMarkEntity.Kind kind = SpellMarkEntity.Kind.SIGIL;
        public int rgb = 0xFFFFFF;
        public float size = 1f;
        public float age;
        public float life = 20f;
        public float yaw;
        public int glyph;
        public float ex, ey, ez;
        public int seed;
    }

    private static final Identifier[] SIGILS = {fx("sigil_0"), fx("sigil_1"), fx("sigil_2"), fx("sigil_3")};
    private static final Identifier RING = fx("ring");
    private static final Identifier PILLAR = fx("pillar");
    private static final Identifier BEAM = fx("beam");
    private static final Identifier GLOW = fx("glow");

    private static Identifier fx(String name) {
        return Identifier.fromNamespaceAndPath(Oathbound.MODID, "textures/effect/" + name + ".png");
    }

    public SpellMarkRenderer(EntityRendererProvider.Context c) {
        super(c);
    }

    @Override
    public State createRenderState() {
        return new State();
    }

    @Override
    public void extractRenderState(SpellMarkEntity e, State s, float pt) {
        super.extractRenderState(e, s, pt);
        s.kind = e.kind();
        s.rgb = e.hue().rgb;
        s.size = e.size();
        s.life = Math.max(2, e.life());
        s.age = Math.min(s.life, e.tickCount + pt);
        s.yaw = e.getYRot();
        s.glyph = e.glyph();
        Vec3 end = e.end();
        s.ex = (float) end.x;
        s.ey = (float) end.y;
        s.ez = (float) end.z;
        s.seed = e.getId();
    }

    @Override
    protected boolean affectedByCulling(SpellMarkEntity e) {
        return false;
    }

    @Override
    public void submit(State s, PoseStack pose, SubmitNodeCollector collector, CameraRenderState camera) {
        float fade = Mth.clamp(s.age / 5f, 0f, 1f) * Mth.clamp((s.life - s.age) / 8f, 0f, 1f);
        if (fade > 0.01f) {
            switch (s.kind) {
                case SIGIL -> sigil(s, pose, collector, fade, false);
                case WALL_SIGIL -> sigil(s, pose, collector, fade, true);
                case PILLAR -> pillar(s, pose, collector, fade);
                case RING -> ring(s, pose, collector, fade);
                case BEAM -> beam(s, pose, collector, fade);
                case HALO -> halo(s, pose, collector, fade);
            }
        }
        super.submit(s, pose, collector, camera);
    }

    // ------------------------------------------------------------------ the five shapes
    /** Two counter-rotating rune circles and a soft bloom beneath them; it swells in and spins faster as it dies. */
    private static void sigil(State s, PoseStack pose, SubmitNodeCollector c, float fade, boolean upright) {
        float t = s.age / s.life;
        float grow = 0.55f + 0.45f * ease(Mth.clamp(s.age / 7f, 0f, 1f));
        float r = s.size * grow;
        float spin = s.age * (0.035f + t * 0.05f);
        pose.pushPose();
        if (upright) {
            pose.mulPose(com.mojang.math.Axis.YP.rotationDegrees(-s.yaw));
            pose.mulPose(com.mojang.math.Axis.XP.rotationDegrees(90f));
        }
        int col = tint(s.rgb, fade);
        int soft = tint(s.rgb, fade * 0.45f);
        int inner = tint(lighten(s.rgb, 0.45f), fade * 0.9f);
        c.submitCustomGeometry(pose, RenderTypes.eyes(GLOW), (p, vc) -> flatQuad(vc, p, r * 1.25f, 0f, 0.01f, soft));
        c.submitCustomGeometry(pose, RenderTypes.eyes(SIGILS[s.glyph & 3]), (p, vc) -> flatQuad(vc, p, r, spin, 0.02f, col));
        c.submitCustomGeometry(pose, RenderTypes.eyes(SIGILS[(s.glyph + 1) & 3]), (p, vc) -> flatQuad(vc, p, r * 0.58f, -spin * 1.7f, 0.03f, inner));
        pose.popPose();
    }

    /** A column of light: a bright core, a wider haze, and bands of light climbing it. */
    private static void pillar(State s, PoseStack pose, SubmitNodeCollector c, float fade) {
        float t = s.age / s.life;
        float r = s.size * (t > 0.7f ? 1f - (t - 0.7f) / 0.3f * 0.8f : 1f);
        float h = Math.min(40f, s.size * 12f);
        int core = tint(lighten(s.rgb, 0.5f), fade);
        int haze = tint(s.rgb, fade * 0.5f);
        c.submitCustomGeometry(pose, RenderTypes.eyes(PILLAR), (p, vc) -> {
            tube(vc, p, r * 0.55f, r * 0.45f, 0f, h, 16, core, 0f, 1f);
            tube(vc, p, r * 1.15f, r * 0.9f, 0f, h * 0.8f, 16, haze, 0f, 1f);
        });
        c.submitCustomGeometry(pose, RenderTypes.eyes(RING), (p, vc) -> {
            for (int i = 0; i < 3; i++) {
                float k = ((s.age * 0.045f) + i / 3f) % 1f;
                float y = k * h * 0.85f;
                int band = tint(s.rgb, fade * (1f - k));
                tube(vc, p, r * (1.3f - k * 0.5f), r * (1.3f - k * 0.5f), y, y + 0.35f, 16, band, 0f, 1f);
            }
        });
        c.submitCustomGeometry(pose, RenderTypes.eyes(GLOW), (p, vc) -> flatQuad(vc, p, r * 2.4f, 0f, 0.02f, tint(s.rgb, fade * 0.6f)));
    }

    /** A shockwave: a flat ring that races outward and a short wall of light standing on its edge. */
    private static void ring(State s, PoseStack pose, SubmitNodeCollector c, float fade) {
        float t = s.age / s.life;
        float r = Math.max(0.2f, s.size * ease(t));
        float band = 0.35f + s.size * 0.08f;
        float f = fade * (1f - t * 0.6f);
        int col = tint(s.rgb, f);
        int wall = tint(lighten(s.rgb, 0.3f), f * 0.7f);
        c.submitCustomGeometry(pose, RenderTypes.eyes(RING), (p, vc) -> {
            annulus(vc, p, Math.max(0f, r - band), r + band * 0.4f, 0.02f, 48, col);
            tube(vc, p, r, r * 1.02f, 0f, 0.3f + (1f - t) * 1.1f, 48, wall, 0f, 1f);
        });
    }

    /** A forked beam from here to the end point, re-forking a few times a second. */
    private static void beam(State s, PoseStack pose, SubmitNodeCollector c, float fade) {
        Vec3 d = new Vec3(s.ex, s.ey, s.ez);
        double len = d.length();
        if (len < 0.01) return;
        int segs = Math.max(4, (int) (len * 1.5));
        int frame = (int) (s.age * 0.6f);
        java.util.Random rnd = new java.util.Random(s.seed * 31L + frame);
        Vec3[] pts = new Vec3[segs + 1];
        Vec3 dir = d.normalize();
        Vec3 side = Math.abs(dir.y) > 0.9 ? new Vec3(1, 0, 0) : dir.cross(new Vec3(0, 1, 0)).normalize();
        Vec3 up = side.cross(dir).normalize();
        for (int i = 0; i <= segs; i++) {
            double k = i / (double) segs;
            double jitter = (i == 0 || i == segs) ? 0 : 0.35 * Math.sin(k * Math.PI);
            pts[i] = d.scale(k).add(side.scale((rnd.nextDouble() - 0.5) * jitter)).add(up.scale((rnd.nextDouble() - 0.5) * jitter));
        }
        float w = s.size;
        int core = tint(lighten(s.rgb, 0.6f), fade);
        int glow = tint(s.rgb, fade * 0.7f);
        c.submitCustomGeometry(pose, RenderTypes.eyes(BEAM), (p, vc) -> {
            for (int i = 0; i < segs; i++) {
                float u0 = i / (float) segs, u1 = (i + 1) / (float) segs;
                ribbon(vc, p, pts[i], pts[i + 1], side, w * 2.6f, glow, u0, u1);
                ribbon(vc, p, pts[i], pts[i + 1], up, w * 2.6f, glow, u0, u1);
                ribbon(vc, p, pts[i], pts[i + 1], side, w, core, u0, u1);
                ribbon(vc, p, pts[i], pts[i + 1], up, w, core, u0, u1);
            }
        });
        c.submitCustomGeometry(pose, RenderTypes.eyes(GLOW), (p, vc) -> flatQuad(vc, p, w * 4f, 0f, 0f, glow));
    }

    /** A crown of light: a slowly turning flat ring with a faint column rising from it. */
    private static void halo(State s, PoseStack pose, SubmitNodeCollector c, float fade) {
        float r = s.size;
        float spin = s.age * 0.05f;
        int col = tint(s.rgb, fade);
        int haze = tint(s.rgb, fade * 0.35f);
        c.submitCustomGeometry(pose, RenderTypes.eyes(RING), (p, vc) -> {
            annulus(vc, p, r * 0.78f, r, 0f, 40, col);
            tube(vc, p, r * 0.9f, r * 0.7f, 0f, r * 1.4f, 24, haze, 0f, 1f);
        });
        c.submitCustomGeometry(pose, RenderTypes.eyes(SIGILS[s.glyph & 3]), (p, vc) -> flatQuad(vc, p, r * 0.9f, spin, 0.01f, tint(s.rgb, fade * 0.5f)));
    }

    // ------------------------------------------------------------------ glowing projectiles
    /** A projectile drawn as a ball of light: three crossed glow planes around a white-hot core, slowly turning. */
    public static class Orb<T extends net.minecraft.world.entity.Entity> extends EntityRenderer<T, State> {
        private final int rgb;
        private final float radius;

        public Orb(EntityRendererProvider.Context c, int rgb, float radius) {
            super(c);
            this.rgb = rgb;
            this.radius = radius;
        }

        @Override
        public State createRenderState() {
            return new State();
        }

        @Override
        public void extractRenderState(T e, State s, float pt) {
            super.extractRenderState(e, s, pt);
            s.age = e.tickCount + pt;
            s.size = e.getBbHeight() / 2f;
        }

        @Override
        public void submit(State s, PoseStack pose, SubmitNodeCollector c, CameraRenderState camera) {
            pose.pushPose();
            pose.translate(0f, s.size, 0f);
            pose.mulPose(com.mojang.math.Axis.YP.rotation(s.age * 0.2f));
            float pulse = 1f + Mth.sin(s.age * 0.9f) * 0.12f;
            float r = radius * pulse;
            int outer = tint(rgb, 0.85f);
            int core = tint(lighten(rgb, 0.8f), 1f);
            c.submitCustomGeometry(pose, RenderTypes.eyes(GLOW), (p, vc) -> {
                crossed(vc, p, r * 2.2f, outer);
                crossed(vc, p, r * 0.9f, core);
            });
            pose.popPose();
            super.submit(s, pose, c, camera);
        }

        private static void crossed(VertexConsumer vc, PoseStack.Pose p, float r, int color) {
            flatQuad(vc, p, r, 0f, 0f, color);
            // the two upright planes
            vtx(vc, p, -r, -r, 0, 0, 1, color);
            vtx(vc, p, r, -r, 0, 1, 1, color);
            vtx(vc, p, r, r, 0, 1, 0, color);
            vtx(vc, p, -r, r, 0, 0, 0, color);
            vtx(vc, p, -r, r, 0, 0, 0, color);
            vtx(vc, p, r, r, 0, 1, 0, color);
            vtx(vc, p, r, -r, 0, 1, 1, color);
            vtx(vc, p, -r, -r, 0, 0, 1, color);
            vtx(vc, p, 0, -r, -r, 0, 1, color);
            vtx(vc, p, 0, -r, r, 1, 1, color);
            vtx(vc, p, 0, r, r, 1, 0, color);
            vtx(vc, p, 0, r, -r, 0, 0, color);
            vtx(vc, p, 0, r, -r, 0, 0, color);
            vtx(vc, p, 0, r, r, 1, 0, color);
            vtx(vc, p, 0, -r, r, 1, 1, color);
            vtx(vc, p, 0, -r, -r, 0, 1, color);
        }
    }

    // ------------------------------------------------------------------ geometry helpers
    /** A square lying flat, turned by {@code angle}, drawn from both sides. */
    private static void flatQuad(VertexConsumer vc, PoseStack.Pose p, float r, float angle, float y, int color) {
        float cs = Mth.cos(angle) * r, sn = Mth.sin(angle) * r;
        float ax = -cs + sn, az = -sn - cs;
        float bx = cs + sn, bz = sn - cs;
        vtx(vc, p, ax, y, az, 0, 0, color);
        vtx(vc, p, -bx, y, -bz, 0, 1, color);
        vtx(vc, p, -ax, y, -az, 1, 1, color);
        vtx(vc, p, bx, y, bz, 1, 0, color);
        vtx(vc, p, bx, y, bz, 1, 0, color);
        vtx(vc, p, -ax, y, -az, 1, 1, color);
        vtx(vc, p, -bx, y, -bz, 0, 1, color);
        vtx(vc, p, ax, y, az, 0, 0, color);
    }

    /** An open cylinder (or cone) from y0 to y1, texture v running bottom (1) to top (0); drawn from both sides. */
    private static void tube(VertexConsumer vc, PoseStack.Pose p, float r0, float r1, float y0, float y1, int n, int color, float vBottom, float vTop) {
        for (int i = 0; i < n; i++) {
            float a0 = i * Mth.TWO_PI / n, a1 = (i + 1) * Mth.TWO_PI / n;
            float u0 = i / (float) n, u1 = (i + 1) / (float) n;
            float c0 = Mth.cos(a0), s0 = Mth.sin(a0), c1 = Mth.cos(a1), s1 = Mth.sin(a1);
            vtx(vc, p, c0 * r0, y0, s0 * r0, u0, 1, color);
            vtx(vc, p, c1 * r0, y0, s1 * r0, u1, 1, color);
            vtx(vc, p, c1 * r1, y1, s1 * r1, u1, 0, color);
            vtx(vc, p, c0 * r1, y1, s0 * r1, u0, 0, color);
            vtx(vc, p, c0 * r1, y1, s0 * r1, u0, 0, color);
            vtx(vc, p, c1 * r1, y1, s1 * r1, u1, 0, color);
            vtx(vc, p, c1 * r0, y0, s1 * r0, u1, 1, color);
            vtx(vc, p, c0 * r0, y0, s0 * r0, u0, 1, color);
        }
    }

    /** A flat ring between two radii, texture v running inner (0) to outer (1); drawn from both sides. */
    private static void annulus(VertexConsumer vc, PoseStack.Pose p, float rin, float rout, float y, int n, int color) {
        for (int i = 0; i < n; i++) {
            float a0 = i * Mth.TWO_PI / n, a1 = (i + 1) * Mth.TWO_PI / n;
            float u0 = i / (float) n, u1 = (i + 1) / (float) n;
            float c0 = Mth.cos(a0), s0 = Mth.sin(a0), c1 = Mth.cos(a1), s1 = Mth.sin(a1);
            vtx(vc, p, c0 * rin, y, s0 * rin, u0, 0, color);
            vtx(vc, p, c0 * rout, y, s0 * rout, u0, 1, color);
            vtx(vc, p, c1 * rout, y, s1 * rout, u1, 1, color);
            vtx(vc, p, c1 * rin, y, s1 * rin, u1, 0, color);
            vtx(vc, p, c1 * rin, y, s1 * rin, u1, 0, color);
            vtx(vc, p, c1 * rout, y, s1 * rout, u1, 1, color);
            vtx(vc, p, c0 * rout, y, s0 * rout, u0, 1, color);
            vtx(vc, p, c0 * rin, y, s0 * rin, u0, 0, color);
        }
    }

    /** One segment of a beam: a strip between two points, widened along {@code across}. */
    private static void ribbon(VertexConsumer vc, PoseStack.Pose p, Vec3 a, Vec3 b, Vec3 across, float width, int color, float u0, float u1) {
        float hx = (float) across.x * width / 2, hy = (float) across.y * width / 2, hz = (float) across.z * width / 2;
        float ax = (float) a.x, ay = (float) a.y, az = (float) a.z, bx = (float) b.x, by = (float) b.y, bz = (float) b.z;
        vtx(vc, p, ax - hx, ay - hy, az - hz, u0, 0, color);
        vtx(vc, p, bx - hx, by - hy, bz - hz, u1, 0, color);
        vtx(vc, p, bx + hx, by + hy, bz + hz, u1, 1, color);
        vtx(vc, p, ax + hx, ay + hy, az + hz, u0, 1, color);
        vtx(vc, p, ax + hx, ay + hy, az + hz, u0, 1, color);
        vtx(vc, p, bx + hx, by + hy, bz + hz, u1, 1, color);
        vtx(vc, p, bx - hx, by - hy, bz - hz, u1, 0, color);
        vtx(vc, p, ax - hx, ay - hy, az - hz, u0, 0, color);
    }

    private static void vtx(VertexConsumer vc, PoseStack.Pose p, float x, float y, float z, float u, float v, int color) {
        vc.addVertex(p, x, y, z).setColor(color).setUv(u, v).setOverlay(OverlayTexture.NO_OVERLAY)
            .setLight(LightCoordsUtil.FULL_BRIGHT).setNormal(p, 0f, 1f, 0f);
    }

    // ------------------------------------------------------------------ colour
    /** ARGB with both the colour and the alpha scaled, so the fade works whether the blend is additive or not. */
    private static int tint(int rgb, float f) {
        f = Mth.clamp(f, 0f, 1f);
        int r = (int) (((rgb >> 16) & 255) * f), g = (int) (((rgb >> 8) & 255) * f), b = (int) ((rgb & 255) * f);
        return ((int) (255 * f) << 24) | (r << 16) | (g << 8) | b;
    }

    private static int lighten(int rgb, float k) {
        int r = (rgb >> 16) & 255, g = (rgb >> 8) & 255, b = rgb & 255;
        r += (int) ((255 - r) * k);
        g += (int) ((255 - g) * k);
        b += (int) ((255 - b) * k);
        return (r << 16) | (g << 8) | b;
    }

    private static float ease(float t) {
        float u = 1f - t;
        return 1f - u * u * u;
    }

}
