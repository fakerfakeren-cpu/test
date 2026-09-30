package com.oathbound.client;

import com.oathbound.client.model.ModelDefs;
import com.oathbound.client.particle.GlimmerParticle;
import com.oathbound.client.particle.GlimmerParticle.Recipe;
import com.oathbound.client.render.Renderers;
import com.oathbound.client.render.SpellMarkRenderer;
import com.oathbound.registry.ModEntities;
import com.oathbound.registry.ModParticles;
import net.minecraft.client.renderer.entity.ThrownItemRenderer;
import net.minecraftforge.client.event.EntityRenderersEvent;
import net.minecraftforge.client.event.RegisterParticleProvidersEvent;
import net.minecraftforge.client.event.ScreenEvent;
import net.minecraftforge.client.event.ViewportEvent;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext;

/** Client-only wiring. Loaded only on the physical client. */
public final class ClientSetup {
    private ClientSetup() {}

    public static void init(FMLJavaModLoadingContext context) {
        EntityRenderersEvent.RegisterLayerDefinitions.BUS.addListener(e -> ModelDefs.register(e::registerLayerDefinition));
        EntityRenderersEvent.RegisterRenderers.BUS.addListener(ClientSetup::renderers);
        RegisterParticleProvidersEvent.BUS.addListener(ClientSetup::particles);
        ViewportEvent.ComputeCameraAngles.BUS.addListener(Atmosphere::onCameraAngles);
        ViewportEvent.ComputeFogColor.BUS.addListener(Atmosphere::onFogColor);
        TickEvent.ClientTickEvent.Post.BUS.addListener(Atmosphere::onClientTick);
        TickEvent.ClientTickEvent.Post.BUS.addListener(Ambience::onClientTick);
        ScreenEvent.Opening.BUS.addListener(PromptAnswerer::onScreenOpening);
        TickEvent.ClientTickEvent.Post.BUS.addListener(PromptAnswerer::onClientTick);
        if (Showcase.enabled()) {
            TickEvent.ClientTickEvent.Post.BUS.addListener(Showcase::onClientTick);
            Showcase.startWatchdog();
        }
    }

    private static void renderers(EntityRenderersEvent.RegisterRenderers e) {
        e.registerEntityRenderer(ModEntities.LANTERNMOTH.get(), Renderers.Moth::new);
        e.registerEntityRenderer(ModEntities.GLOAMLING.get(), Renderers.Gloamling::new);
        e.registerEntityRenderer(ModEntities.FORSWORN_KNIGHT.get(), Renderers.Knight::new);
        e.registerEntityRenderer(ModEntities.BARROW_WIGHT.get(), Renderers.Wight::new);
        e.registerEntityRenderer(ModEntities.ANIMATED_TOME.get(), Renderers.Tome::new);
        e.registerEntityRenderer(ModEntities.VEILHOUND.get(), Renderers.Hound::new);
        e.registerEntityRenderer(ModEntities.SPECTRAL_HOUSECARL.get(), Renderers.Housecarl::new);
        e.registerEntityRenderer(ModEntities.SIR_CALDRIS.get(), Renderers.caldris());
        e.registerEntityRenderer(ModEntities.ARCHMAGE_VEYL.get(), Renderers.veyl());
        e.registerEntityRenderer(ModEntities.HRODGAR.get(), Renderers.hrodgar());
        e.registerEntityRenderer(ModEntities.MORVANE.get(), Renderers.morvane());
        e.registerEntityRenderer(ModEntities.CROWN_BLADE.get(), Renderers.Blade::new);
        e.registerEntityRenderer(ModEntities.SPELL_MARK.get(), SpellMarkRenderer::new);
        e.registerEntityRenderer(ModEntities.ARCANE_ORB.get(), c -> new SpellMarkRenderer.Orb<>(c, 0x6FA8FF, 0.32f));
        e.registerEntityRenderer(ModEntities.GLYPH_BOLT.get(), c -> new SpellMarkRenderer.Orb<>(c, 0xB8D4FF, 0.2f));
        e.registerEntityRenderer(ModEntities.GLOAM_BOLT.get(), c -> new SpellMarkRenderer.Orb<>(c, 0xA35CFF, 0.26f));
        e.registerEntityRenderer(ModEntities.SUN_ARROW.get(), c -> new SpellMarkRenderer.Orb<>(c, 0xFFD36B, 0.16f));
        e.registerEntityRenderer(ModEntities.ANCHOR_HOOK.get(), c -> new ThrownItemRenderer<>(c, 1.4f, true));
        e.registerEntityRenderer(ModEntities.LUMEN_FLASK.get(), ThrownItemRenderer::new);
        RosterRenderers.register(e);
    }

    private static void particles(RegisterParticleProvidersEvent e) {
        //                                                                      birth      death     lift   life size spin drag
        e.registerSpriteSet(ModParticles.EMBER.get(), s -> GlimmerParticle.provider(s, new Recipe(0xFFD27A, 0xC0391B, 0.004f, 22, 0.9f, 0.3f, 0.94f)));
        e.registerSpriteSet(ModParticles.LUMEN_MOTE.get(), s -> GlimmerParticle.provider(s, new Recipe(0xFFF4C2, 0xE8B04A, 0.0f, 30, 1.0f, 0.1f, 0.92f)));
        e.registerSpriteSet(ModParticles.GLOAM_WISP.get(), s -> GlimmerParticle.provider(s, new Recipe(0x9C6BD8, 0x1A0B2E, 0.002f, 28, 1.5f, 0.2f, 0.9f)));
        e.registerSpriteSet(ModParticles.ARCANE_GLYPH.get(), s -> GlimmerParticle.provider(s, new Recipe(0xB8D4FF, 0x6A3CE0, 0.0f, 20, 1.1f, 0.6f, 0.9f)));
        e.registerSpriteSet(ModParticles.SPIRIT.get(), s -> GlimmerParticle.provider(s, new Recipe(0xB4FFF0, 0x2E8C86, 0.003f, 26, 1.2f, 0.15f, 0.9f)));
        e.registerSpriteSet(ModParticles.SUNBURST.get(), s -> GlimmerParticle.provider(s, new Recipe(0xFFFFFF, 0xFFC247, 0.0f, 16, 1.4f, 0.5f, 0.88f)));
        e.registerSpriteSet(ModParticles.TIDE.get(), s -> GlimmerParticle.provider(s, new Recipe(0x9CF6E0, 0x1E6E7A, -0.004f, 22, 1.0f, 0.2f, 0.9f)));
        e.registerSpriteSet(ModParticles.PETAL.get(), s -> GlimmerParticle.provider(s, new Recipe(0xE4FFB0, 0x5FA83A, -0.006f, 50, 1.1f, 0.25f, 0.95f)));
        e.registerSpriteSet(ModParticles.SPORE.get(), s -> GlimmerParticle.provider(s, new Recipe(0xD8FF8A, 0x1E6B4A, 0.0015f, 40, 1.0f, 0.05f, 0.93f)));
        e.registerSpriteSet(ModParticles.FIREFLY.get(), s -> com.oathbound.client.particle.FireflyParticle.provider(s, new Recipe(0xF6FF9A, 0xB8F04A, 0.0f, 120, 0.6f, 0.0f, 0.97f)));
        e.registerSpriteSet(ModParticles.BLOSSOM.get(), s -> GlimmerParticle.provider(s, new Recipe(0xFFD6EC, 0xF28CC0, -0.004f, 90, 1.0f, 0.3f, 0.97f)));
        e.registerSpriteSet(ModParticles.ASH.get(), s -> GlimmerParticle.provider(s, new Recipe(0xFFB060, 0x3A3430, -0.003f, 60, 0.9f, 0.2f, 0.96f)));
    }
}
