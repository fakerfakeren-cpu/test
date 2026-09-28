package com.astralfall.client.render;

import com.astralfall.Astralfall;
import com.astralfall.client.model.*;
import com.astralfall.entity.MeteorEntity;
import com.astralfall.entity.SingularityEntity;
import com.astralfall.entity.boss.AstraeusEntity;
import com.astralfall.entity.mob.AstralWispEntity;
import com.astralfall.entity.mob.MeteoriteCrawlerEntity;
import com.astralfall.entity.mob.VoidGazerEntity;
import com.astralfall.entity.mob.VoidStalkerEntity;
import com.astralfall.event.Starfall;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import net.minecraft.client.model.geom.ModelLayerLocation;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.MobRenderer;
import net.minecraft.client.renderer.rendertype.RenderTypes;
import net.minecraft.client.renderer.state.level.CameraRenderState;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.Identifier;
import net.minecraft.util.LightCoordsUtil;
import net.minecraft.util.Mth;
import net.minecraft.world.phys.AABB;

/** All Astralfall entity renderers. */
public final class Renderers {
    public static final ModelLayerLocation WISP = layer("astral_wisp");
    public static final ModelLayerLocation STALKER = layer("void_stalker");
    public static final ModelLayerLocation CRAWLER = layer("meteorite_crawler");
    public static final ModelLayerLocation GAZER = layer("void_gazer");
    public static final ModelLayerLocation ASTRAEUS = layer("astraeus");
    public static final ModelLayerLocation METEOR = layer("meteor");
    public static final ModelLayerLocation METEOR_STAR = layer("meteor_star");
    public static final ModelLayerLocation SINGULARITY = layer("singularity");

    private Renderers() {}

    private static ModelLayerLocation layer(String name) {
        return new ModelLayerLocation(Identifier.fromNamespaceAndPath(Astralfall.MODID, name), "main");
    }

    static Identifier tex(String name) {
        return Identifier.fromNamespaceAndPath(Astralfall.MODID, "textures/entity/" + name + ".png");
    }

    // ------------------------------------------------------------------ wisp
    public static class Wisp extends MobRenderer<AstralWispEntity, States.Wisp, WispModel> {
        private static final Identifier TEX = tex("astral_wisp");

        public Wisp(EntityRendererProvider.Context ctx) {
            super(ctx, new WispModel(ctx.bakeLayer(WISP)), 0.25f);
            addLayer(new GlowLayer<>(this, tex("astral_wisp_glow")));
        }

        @Override
        public States.Wisp createRenderState() {
            return new States.Wisp();
        }

        @Override
        public void extractRenderState(AstralWispEntity e, States.Wisp s, float pt) {
            super.extractRenderState(e, s, pt);
            s.prismatic = e.isPrismatic();
            s.sitting = e.isInSittingPose() || e.isOrderedToSit();
        }

        @Override
        protected int getModelTint(States.Wisp s) {
            if (!s.prismatic) return -1;
            return 0xFF000000 | Mth.hsvToRgb((s.ageInTicks % 80f) / 80f, 0.55f, 1.0f);
        }

        @Override
        public Identifier getTextureLocation(States.Wisp s) {
            return TEX;
        }
    }

    // ------------------------------------------------------------------ stalker
    public static class Stalker extends MobRenderer<VoidStalkerEntity, States.Stalker, StalkerModel> {
        private static final Identifier TEX = tex("void_stalker");

        public Stalker(EntityRendererProvider.Context ctx) {
            super(ctx, new StalkerModel(ctx.bakeLayer(STALKER)), 0.5f);
            addLayer(new GlowLayer<>(this, tex("void_stalker_glow")));
        }

        @Override
        public States.Stalker createRenderState() {
            return new States.Stalker();
        }

        @Override
        public void extractRenderState(VoidStalkerEntity e, States.Stalker s, float pt) {
            super.extractRenderState(e, s, pt);
            s.frozen = e.isFrozen();
            s.attackAnim = e.getAttackAnim(pt);
        }

        @Override
        protected void scale(States.Stalker s, PoseStack pose) {
            pose.scale(1.2f, 1.2f, 1.2f);
        }

        @Override
        public Identifier getTextureLocation(States.Stalker s) {
            return TEX;
        }
    }

    // ------------------------------------------------------------------ crawler
    public static class Crawler extends MobRenderer<MeteoriteCrawlerEntity, States.Crawler, CrawlerModel> {
        private static final Identifier TEX = tex("meteorite_crawler");

        public Crawler(EntityRendererProvider.Context ctx) {
            super(ctx, new CrawlerModel(ctx.bakeLayer(CRAWLER)), 0.8f);
            addLayer(new GlowLayer<>(this, tex("meteorite_crawler_glow")));
        }

        @Override
        public States.Crawler createRenderState() {
            return new States.Crawler();
        }

        @Override
        public void extractRenderState(MeteoriteCrawlerEntity e, States.Crawler s, float pt) {
            super.extractRenderState(e, s, pt);
            s.mode = e.getState();
            s.roll = Mth.lerp(pt, e.rollAngleO, e.rollAngle);
        }

        @Override
        public Identifier getTextureLocation(States.Crawler s) {
            return TEX;
        }
    }

    // ------------------------------------------------------------------ gazer
    public static class Gazer extends MobRenderer<VoidGazerEntity, States.Gazer, GazerModel> {
        private static final Identifier TEX = tex("void_gazer");

        public Gazer(EntityRendererProvider.Context ctx) {
            super(ctx, new GazerModel(ctx.bakeLayer(GAZER)), 0.6f);
            addLayer(new GlowLayer<>(this, tex("void_gazer_glow")));
        }

        @Override
        public States.Gazer createRenderState() {
            return new States.Gazer();
        }

        @Override
        public void extractRenderState(VoidGazerEntity e, States.Gazer s, float pt) {
            super.extractRenderState(e, s, pt);
            s.charge = e.getCharge() / (float) VoidGazerEntity.CHARGE_TIME;
        }

        @Override
        public Identifier getTextureLocation(States.Gazer s) {
            return TEX;
        }
    }

    // ------------------------------------------------------------------ astraeus
    public static class Astraeus extends MobRenderer<AstraeusEntity, States.Titan, AstraeusModel> {
        private static final Identifier TEX = tex("astraeus");

        public Astraeus(EntityRendererProvider.Context ctx) {
            super(ctx, new AstraeusModel(ctx.bakeLayer(ASTRAEUS)), 2.5f);
            addLayer(new GlowLayer<>(this, tex("astraeus_glow")));
        }

        @Override
        public States.Titan createRenderState() {
            return new States.Titan();
        }

        @Override
        public void extractRenderState(AstraeusEntity e, States.Titan s, float pt) {
            super.extractRenderState(e, s, pt);
            s.phase = e.getPhase();
            s.attack = e.getAttack();
            s.attackTicks = e.getAttackTicks() + pt;
            s.emerge = e.getEmerge();
            s.shards = e.getShards();
        }

        @Override
        protected void scale(States.Titan s, PoseStack pose) {
            pose.scale(1.4f, 1.4f, 1.4f);
        }

        @Override
        protected float getFlipDegrees() {
            return 0f;
        }

        @Override
        protected AABB getBoundingBoxForCulling(AstraeusEntity e) {
            return e.getBoundingBox().inflate(8.0);
        }

        @Override
        public Identifier getTextureLocation(States.Titan s) {
            return TEX;
        }
    }

    // ------------------------------------------------------------------ meteor
    public static class Meteor extends EntityRenderer<MeteorEntity, States.Meteor> {
        private static final Identifier TEX = tex("meteor");
        private static final Identifier GLOW = tex("meteor_glow");
        private static final Identifier STAR = tex("meteor_star");
        private static final Identifier STAR_GLOW = tex("meteor_star_glow");
        private final SimpleModels.Meteor model;
        private final SimpleModels.Meteor starModel;

        public Meteor(EntityRendererProvider.Context ctx) {
            super(ctx);
            model = new SimpleModels.Meteor(ctx.bakeLayer(METEOR));
            starModel = new SimpleModels.Meteor(ctx.bakeLayer(METEOR_STAR));
        }

        @Override
        public States.Meteor createRenderState() {
            return new States.Meteor();
        }

        @Override
        public void extractRenderState(MeteorEntity e, States.Meteor s, float pt) {
            super.extractRenderState(e, s, pt);
            s.spin = Mth.lerp(pt, e.spinO, e.spin);
            s.size = e.getSize();
            s.variant = e.getVariant().ordinal();
        }

        @Override
        public void submit(States.Meteor s, PoseStack pose, SubmitNodeCollector collector, CameraRenderState camera) {
            if (s.variant != Starfall.Variant.SHOOTING_STAR.ordinal()) {
                boolean star = s.variant == Starfall.Variant.FALLEN_STAR.ordinal();
                pose.pushPose();
                pose.translate(0, 0.6, 0);
                pose.mulPose(Axis.XP.rotationDegrees(s.spin));
                pose.mulPose(Axis.ZP.rotationDegrees(s.spin * 0.6f));
                float sc = s.size * 0.55f;
                pose.scale(sc, sc, sc);
                SimpleModels.Meteor m = star ? starModel : model;
                collector.submitModel(m, s, pose, RenderTypes.entityCutout(star ? STAR : TEX), LightCoordsUtil.FULL_BRIGHT, OverlayTexture.NO_OVERLAY, s.outlineColor, null);
                collector.submitModel(m, s, pose, RenderTypes.eyes(star ? STAR_GLOW : GLOW), LightCoordsUtil.FULL_BRIGHT, OverlayTexture.NO_OVERLAY, s.outlineColor, null);
                pose.popPose();
            }
            super.submit(s, pose, collector, camera);
        }
    }

    // ------------------------------------------------------------------ singularity
    public static class Singularity extends EntityRenderer<SingularityEntity, States.Singularity> {
        private static final Identifier TEX = tex("singularity");
        private static final Identifier GLOW = tex("singularity_glow");
        private final SimpleModels.Singularity core;
        private final SimpleModels.Singularity disk;

        public Singularity(EntityRendererProvider.Context ctx) {
            super(ctx);
            core = new SimpleModels.Singularity(ctx.bakeLayer(SINGULARITY), false);
            disk = new SimpleModels.Singularity(ctx.bakeLayer(SINGULARITY), true);
        }

        @Override
        public States.Singularity createRenderState() {
            return new States.Singularity();
        }

        @Override
        public void extractRenderState(SingularityEntity e, States.Singularity s, float pt) {
            super.extractRenderState(e, s, pt);
            s.progress = e.getProgress(pt);
            s.radius = e.getRadius();
        }

        @Override
        public void submit(States.Singularity s, PoseStack pose, SubmitNodeCollector collector, CameraRenderState camera) {
            float grow = Mth.clamp(s.progress * 6f, 0f, 1f);
            float collapse = s.progress > 0.9f ? 1f - (s.progress - 0.9f) * 8f : 1f;
            float sc = s.radius * 0.11f * grow * Math.max(0.1f, collapse) * (1f + Mth.sin(s.ageInTicks * 0.4f) * 0.05f);
            pose.pushPose();
            pose.translate(0, 0.5, 0);
            pose.scale(sc, sc, sc);
            collector.submitModel(core, s, pose, RenderTypes.entitySolid(TEX), LightCoordsUtil.FULL_BRIGHT, OverlayTexture.NO_OVERLAY, s.outlineColor, null);
            pose.scale(1.4f, 1.4f, 1.4f);
            collector.submitModel(disk, s, pose, RenderTypes.eyes(GLOW), LightCoordsUtil.FULL_BRIGHT, OverlayTexture.NO_OVERLAY, s.outlineColor, null);
            pose.popPose();
            super.submit(s, pose, collector, camera);
        }
    }
}
