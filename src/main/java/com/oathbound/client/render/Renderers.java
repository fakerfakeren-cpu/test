package com.oathbound.client.render;

import com.mojang.blaze3d.vertex.PoseStack;
import com.oathbound.Oathbound;
import com.oathbound.client.model.CreatureModels;
import com.oathbound.client.model.KeeperModels;
import com.oathbound.entity.boss.*;
import com.oathbound.entity.mob.*;
import com.oathbound.entity.projectile.CrownBladeEntity;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.model.geom.ModelLayerLocation;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.MobRenderer;
import net.minecraft.client.renderer.entity.state.LivingEntityRenderState;
import net.minecraft.client.renderer.rendertype.RenderType;
import net.minecraft.client.renderer.rendertype.RenderTypes;
import net.minecraft.client.renderer.state.level.CameraRenderState;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.Identifier;
import net.minecraft.util.LightCoordsUtil;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.phys.AABB;

import java.util.function.Function;

/** Every Oathbound entity renderer. */
public final class Renderers {
    private Renderers() {}

    public static ModelLayerLocation layer(String name) {
        return new ModelLayerLocation(Identifier.fromNamespaceAndPath(Oathbound.MODID, name), "main");
    }

    static Identifier tex(String name) {
        return Identifier.fromNamespaceAndPath(Oathbound.MODID, "textures/entity/" + name + ".png");
    }

    /**
     * Shared renderer: a model, a base and glow texture, optional scale and optional translucency. Subclasses
     * add the per-frame fields they need.
     */
    public abstract static class Base<E extends Mob, S extends LivingEntityRenderState, M extends EntityModel<S>> extends MobRenderer<E, S, M> {
        protected final Identifier texture;
        private final float scale;

        protected Base(EntityRendererProvider.Context ctx, M model, String name, float shadow, float scale) {
            super(ctx, model, shadow);
            this.texture = tex(name);
            this.scale = scale;
            addLayer(new EmissiveLayer<>(this, tex(name + "_glow")));
        }

        protected boolean ghostly(S s) {
            return false;
        }

        @Override
        protected RenderType getRenderType(S s, boolean bodyVisible, boolean translucent, boolean glowing) {
            if (ghostly(s)) return RenderTypes.entityTranslucent(texture);
            return super.getRenderType(s, bodyVisible, translucent, glowing);
        }

        @Override
        protected void scale(S s, PoseStack pose) {
            if (scale != 1f) pose.scale(scale, scale, scale);
        }

        @Override
        public Identifier getTextureLocation(S s) {
            return texture;
        }
    }

    // ------------------------------------------------------------------ creatures
    public static class Moth extends Base<LanternmothEntity, States.Moth, CreatureModels.Moth> {
        public Moth(EntityRendererProvider.Context c) {
            super(c, new CreatureModels.Moth(c.bakeLayer(layer("lanternmoth"))), "lanternmoth", 0.15f, 1f);
        }

        @Override
        public States.Moth createRenderState() {
            return new States.Moth();
        }
    }

    public static class Gloamling extends Base<GloamlingEntity, States.Gloamling, CreatureModels.Gloamling> {
        public Gloamling(EntityRendererProvider.Context c) {
            super(c, new CreatureModels.Gloamling(c.bakeLayer(layer("gloamling"))), "gloamling", 0.3f, 1f);
        }

        @Override
        public States.Gloamling createRenderState() {
            return new States.Gloamling();
        }

        @Override
        public void extractRenderState(GloamlingEntity e, States.Gloamling s, float pt) {
            super.extractRenderState(e, s, pt);
            s.veiled = e.isVeiled();
            s.attack = e.getAttackAnim(pt);
        }

        @Override
        protected boolean ghostly(States.Gloamling s) {
            return s.veiled;
        }

        @Override
        protected int getModelTint(States.Gloamling s) {
            return s.veiled ? 0x30FFFFFF : -1;
        }
    }

    public static class Knight extends Base<ForswornKnightEntity, States.Knight, CreatureModels.Knight> {
        public Knight(EntityRendererProvider.Context c) {
            super(c, new CreatureModels.Knight(c.bakeLayer(layer("forsworn_knight"))), "forsworn_knight", 0.5f, 1f);
        }

        @Override
        public States.Knight createRenderState() {
            return new States.Knight();
        }

        @Override
        public void extractRenderState(ForswornKnightEntity e, States.Knight s, float pt) {
            super.extractRenderState(e, s, pt);
            s.fallen = e.isFallen();
            s.fallenTicks = e.fallenTicks();
            s.attack = e.getAttackAnim(pt);
        }
    }

    public static class Wight extends Base<BarrowWightEntity, States.Wight, CreatureModels.Wight> {
        public Wight(EntityRendererProvider.Context c) {
            super(c, new CreatureModels.Wight(c.bakeLayer(layer("barrow_wight"))), "barrow_wight", 0f, 1f);
        }

        @Override
        public States.Wight createRenderState() {
            return new States.Wight();
        }

        @Override
        protected boolean ghostly(States.Wight s) {
            return true;
        }

        @Override
        protected int getModelTint(States.Wight s) {
            return 0xB0FFFFFF;
        }
    }

    public static class Tome extends Base<AnimatedTomeEntity, States.Tome, CreatureModels.Tome> {
        public Tome(EntityRendererProvider.Context c) {
            super(c, new CreatureModels.Tome(c.bakeLayer(layer("animated_tome"))), "animated_tome", 0.2f, 1f);
        }

        @Override
        public States.Tome createRenderState() {
            return new States.Tome();
        }

        @Override
        public void extractRenderState(AnimatedTomeEntity e, States.Tome s, float pt) {
            super.extractRenderState(e, s, pt);
            s.casting = e.casting();
        }
    }

    public static class Hound extends Base<VeilhoundEntity, States.Hound, CreatureModels.Hound> {
        public Hound(EntityRendererProvider.Context c) {
            super(c, new CreatureModels.Hound(c.bakeLayer(layer("veilhound"))), "veilhound", 0.5f, 1f);
        }

        @Override
        public States.Hound createRenderState() {
            return new States.Hound();
        }

        @Override
        public void extractRenderState(VeilhoundEntity e, States.Hound s, float pt) {
            super.extractRenderState(e, s, pt);
            s.lunging = e.isLunging();
        }
    }

    public static class Housecarl extends Base<SpectralHousecarlEntity, States.Housecarl, CreatureModels.Housecarl> {
        public Housecarl(EntityRendererProvider.Context c) {
            super(c, new CreatureModels.Housecarl(c.bakeLayer(layer("spectral_housecarl"))), "spectral_housecarl", 0f, 1f);
        }

        @Override
        public States.Housecarl createRenderState() {
            return new States.Housecarl();
        }

        @Override
        public void extractRenderState(SpectralHousecarlEntity e, States.Housecarl s, float pt) {
            super.extractRenderState(e, s, pt);
            s.ally = e.isAlly();
            s.attack = e.getAttackAnim(pt);
        }

        @Override
        protected boolean ghostly(States.Housecarl s) {
            return true;
        }

        @Override
        protected int getModelTint(States.Housecarl s) {
            return s.ally ? 0xC0FFE9A8 : 0xB0FFFFFF;
        }
    }

    // ------------------------------------------------------------------ keepers
    public static class Keeper<E extends KeeperEntity, M extends EntityModel<States.Keeper>> extends Base<E, States.Keeper, M> {
        public Keeper(EntityRendererProvider.Context c, Function<net.minecraft.client.model.geom.ModelPart, M> model, String name, float shadow, float scale) {
            super(c, model.apply(c.bakeLayer(layer(name))), name, shadow, scale);
        }

        @Override
        public States.Keeper createRenderState() {
            return new States.Keeper();
        }

        @Override
        public void extractRenderState(E e, States.Keeper s, float pt) {
            super.extractRenderState(e, s, pt);
            s.sleeping = e.isSleeping();
            s.move = e.move();
            s.moveTicks = e.moveTicks() + pt;
            if (e instanceof SirCaldrisEntity c) s.stagger = c.stagger();
            if (e instanceof ArchmageVeylEntity v) s.illusion = v.isIllusion();
            if (e instanceof HrodgarEntity h) s.tethers = h.tethers();
            if (e instanceof MorvaneEntity m) {
                s.phase = m.phase();
                s.hollow = m.isHollow();
            }
        }

        @Override
        protected boolean ghostly(States.Keeper s) {
            return s.illusion || s.hollow;
        }

        @Override
        protected int getModelTint(States.Keeper s) {
            if (s.hollow) return 0x70504070;
            if (s.illusion) return 0xC0D8D0FF;
            return -1;
        }

        @Override
        protected float getFlipDegrees() {
            return 0f;
        }

        @Override
        protected AABB getBoundingBoxForCulling(E e) {
            return e.getBoundingBox().inflate(4.0);
        }
    }

    public static EntityRendererProvider<SirCaldrisEntity> caldris() {
        return c -> new Keeper<>(c, KeeperModels.Caldris::new, "sir_caldris", 0.8f, 1.1f);
    }

    public static EntityRendererProvider<ArchmageVeylEntity> veyl() {
        return c -> new Keeper<>(c, KeeperModels.Veyl::new, "archmage_veyl", 0.6f, 1.05f);
    }

    public static EntityRendererProvider<HrodgarEntity> hrodgar() {
        return c -> new Keeper<>(c, KeeperModels.Hrodgar::new, "hrodgar", 1.2f, 1.35f);
    }

    public static EntityRendererProvider<MorvaneEntity> morvane() {
        return c -> new Keeper<>(c, KeeperModels.Morvane::new, "morvane", 1.0f, 1.3f);
    }

    // ------------------------------------------------------------------ the Crown of Blades
    public static class Blade extends EntityRenderer<CrownBladeEntity, States.Blade> {
        private static final Identifier TEX = tex("crown_blade");
        private static final Identifier GLOW = tex("crown_blade_glow");
        private final CreatureModels.Blade model;

        public Blade(EntityRendererProvider.Context c) {
            super(c);
            model = new CreatureModels.Blade(c.bakeLayer(layer("crown_blade")));
        }

        @Override
        public States.Blade createRenderState() {
            return new States.Blade();
        }

        @Override
        public void extractRenderState(CrownBladeEntity e, States.Blade s, float pt) {
            super.extractRenderState(e, s, pt);
            s.launched = e.isLaunched();
            var v = e.getDeltaMovement();
            s.yaw = (float) (Mth.atan2(v.x, v.z) * Mth.RAD_TO_DEG);
            s.pitch = (float) (Mth.atan2(v.y, v.horizontalDistance()) * Mth.RAD_TO_DEG);
        }

        @Override
        public void submit(States.Blade s, PoseStack pose, SubmitNodeCollector collector, CameraRenderState camera) {
            pose.pushPose();
            pose.translate(0f, 0.25f, 0f);
            model.setupAnim(s);
            collector.submitModel(model, s, pose, RenderTypes.entityCutout(TEX), LightCoordsUtil.FULL_BRIGHT, OverlayTexture.NO_OVERLAY, s.outlineColor, null);
            collector.submitModel(model, s, pose, RenderTypes.eyes(GLOW), LightCoordsUtil.FULL_BRIGHT, OverlayTexture.NO_OVERLAY, s.outlineColor, null);
            pose.popPose();
            super.submit(s, pose, collector, camera);
        }
    }
}
