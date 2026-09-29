package com.rimeheart.client.render;

import com.rimeheart.Rimeheart;
import com.rimeheart.client.model.ShardlingModel;
import com.rimeheart.client.model.SovereignModel;
import com.rimeheart.client.model.WraithModel;
import com.rimeheart.entity.boss.FrostSovereignEntity;
import com.rimeheart.entity.mob.FrostWraithEntity;
import com.rimeheart.entity.mob.ShardlingEntity;
import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.model.geom.ModelLayerLocation;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.MobRenderer;
import net.minecraft.resources.Identifier;
import net.minecraft.world.phys.AABB;

/** All Rimeheart mob renderers (projectiles use vanilla's thrown-item renderer). */
public final class Renderers {
    public static final ModelLayerLocation WRAITH = layer("frost_wraith");
    public static final ModelLayerLocation SHARDLING = layer("shardling");
    public static final ModelLayerLocation SOVEREIGN = layer("frost_sovereign");

    private Renderers() {}

    private static ModelLayerLocation layer(String name) {
        return new ModelLayerLocation(Identifier.fromNamespaceAndPath(Rimeheart.MODID, name), "main");
    }

    static Identifier tex(String name) {
        return Identifier.fromNamespaceAndPath(Rimeheart.MODID, "textures/entity/" + name + ".png");
    }

    public static class Wraith extends MobRenderer<FrostWraithEntity, States.Wraith, WraithModel> {
        private static final Identifier TEX = tex("frost_wraith");

        public Wraith(EntityRendererProvider.Context ctx) {
            super(ctx, new WraithModel(ctx.bakeLayer(WRAITH)), 0.4f);
            addLayer(new GlowLayer<>(this, tex("frost_wraith_glow")));
        }

        @Override
        public States.Wraith createRenderState() {
            return new States.Wraith();
        }

        @Override
        public void extractRenderState(FrostWraithEntity e, States.Wraith s, float pt) {
            super.extractRenderState(e, s, pt);
            s.casting = e.getCasting();
        }

        @Override
        public Identifier getTextureLocation(States.Wraith s) {
            return TEX;
        }
    }

    public static class Shardling extends MobRenderer<ShardlingEntity, States.Shardling, ShardlingModel> {
        private static final Identifier TEX = tex("shardling");

        public Shardling(EntityRendererProvider.Context ctx) {
            super(ctx, new ShardlingModel(ctx.bakeLayer(SHARDLING)), 0.35f);
            addLayer(new GlowLayer<>(this, tex("shardling_glow")));
        }

        @Override
        public States.Shardling createRenderState() {
            return new States.Shardling();
        }

        @Override
        public Identifier getTextureLocation(States.Shardling s) {
            return TEX;
        }
    }

    public static class Sovereign extends MobRenderer<FrostSovereignEntity, States.Sovereign, SovereignModel> {
        private static final Identifier TEX = tex("frost_sovereign");

        public Sovereign(EntityRendererProvider.Context ctx) {
            super(ctx, new SovereignModel(ctx.bakeLayer(SOVEREIGN)), 2.0f);
            addLayer(new GlowLayer<>(this, tex("frost_sovereign_glow")));
        }

        @Override
        public States.Sovereign createRenderState() {
            return new States.Sovereign();
        }

        @Override
        public void extractRenderState(FrostSovereignEntity e, States.Sovereign s, float pt) {
            super.extractRenderState(e, s, pt);
            s.phase = e.getPhase();
            s.attack = e.getAttack();
            s.attackTicks = e.getAttackTicks() + pt;
            s.emerge = e.getEmerge();
        }

        @Override
        protected void scale(States.Sovereign s, PoseStack pose) {
            pose.scale(1.4f, 1.4f, 1.4f);
        }

        @Override
        protected float getFlipDegrees() {
            return 0f;
        }

        @Override
        protected AABB getBoundingBoxForCulling(FrostSovereignEntity e) {
            return e.getBoundingBox().inflate(6.0);
        }

        @Override
        public Identifier getTextureLocation(States.Sovereign s) {
            return TEX;
        }
    }
}
