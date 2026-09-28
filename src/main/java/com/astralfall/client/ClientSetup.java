package com.astralfall.client;

import com.astralfall.client.model.ModelDefs;
import com.astralfall.client.particle.AstralParticle;
import com.astralfall.client.render.Renderers;
import com.astralfall.registry.ModEntities;
import com.astralfall.registry.ModParticles;
import net.minecraft.client.renderer.entity.NoopRenderer;
import net.minecraft.client.renderer.entity.ThrownItemRenderer;
import net.minecraftforge.client.event.EntityRenderersEvent;
import net.minecraftforge.client.event.RegisterParticleProvidersEvent;
import net.minecraftforge.client.event.ScreenEvent;
import net.minecraftforge.client.event.ViewportEvent;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext;

/** Client-only registration. Only ever loaded on the physical client. */
public final class ClientSetup {
    private ClientSetup() {}

    public static void init(FMLJavaModLoadingContext context) {
        EntityRenderersEvent.RegisterLayerDefinitions.BUS.addListener(ClientSetup::layers);
        EntityRenderersEvent.RegisterRenderers.BUS.addListener(ClientSetup::renderers);
        RegisterParticleProvidersEvent.BUS.addListener(ClientSetup::particles);
        ViewportEvent.ComputeCameraAngles.BUS.addListener(ClientFX::onCameraAngles);
        ViewportEvent.ComputeFogColor.BUS.addListener(ClientFX::onFogColor);
        TickEvent.ClientTickEvent.Post.BUS.addListener(ClientFX::onClientTick);
        ScreenEvent.Opening.BUS.addListener(ExperimentalWarningSkipper::onScreenOpening);
        TickEvent.ClientTickEvent.Post.BUS.addListener(ExperimentalWarningSkipper::onClientTick);
        if (ClientTest.enabled()) {
            TickEvent.ClientTickEvent.Post.BUS.addListener(ClientTest::onClientTick);
            ClientTest.startWatchdog();
        }
    }

    private static void layers(EntityRenderersEvent.RegisterLayerDefinitions e) {
        e.registerLayerDefinition(Renderers.WISP, ModelDefs::createAstralWisp);
        e.registerLayerDefinition(Renderers.STALKER, ModelDefs::createVoidStalker);
        e.registerLayerDefinition(Renderers.CRAWLER, ModelDefs::createMeteoriteCrawler);
        e.registerLayerDefinition(Renderers.GAZER, ModelDefs::createVoidGazer);
        e.registerLayerDefinition(Renderers.ASTRAEUS, ModelDefs::createAstraeus);
        e.registerLayerDefinition(Renderers.METEOR, ModelDefs::createMeteor);
        e.registerLayerDefinition(Renderers.METEOR_STAR, ModelDefs::createMeteorStar);
        e.registerLayerDefinition(Renderers.SINGULARITY, ModelDefs::createSingularity);
    }

    private static void renderers(EntityRenderersEvent.RegisterRenderers e) {
        e.registerEntityRenderer(ModEntities.ASTRAL_WISP.get(), Renderers.Wisp::new);
        e.registerEntityRenderer(ModEntities.VOID_STALKER.get(), Renderers.Stalker::new);
        e.registerEntityRenderer(ModEntities.METEORITE_CRAWLER.get(), Renderers.Crawler::new);
        e.registerEntityRenderer(ModEntities.VOID_GAZER.get(), Renderers.Gazer::new);
        e.registerEntityRenderer(ModEntities.ASTRAEUS.get(), Renderers.Astraeus::new);
        e.registerEntityRenderer(ModEntities.METEOR.get(), Renderers.Meteor::new);
        e.registerEntityRenderer(ModEntities.SINGULARITY.get(), Renderers.Singularity::new);
        e.registerEntityRenderer(ModEntities.STAR_SLASH.get(), NoopRenderer::new);
        e.registerEntityRenderer(ModEntities.STAR_BOLT.get(), NoopRenderer::new);
        e.registerEntityRenderer(ModEntities.CRYSTAL_SHARD.get(), ctx -> new ThrownItemRenderer<>(ctx, 1.75f, true));
        e.registerEntityRenderer(ModEntities.SINGULARITY_GRENADE.get(), ThrownItemRenderer::new);
    }

    private static void particles(RegisterParticleProvidersEvent e) {
        e.registerSpriteSet(ModParticles.STAR_SPARKLE.get(), s -> AstralParticle.provider(s, 0x9AF3FF, 0x3FC6E0, 0.0f, 14, 1.0f));
        e.registerSpriteSet(ModParticles.GOLD_SPARKLE.get(), s -> AstralParticle.provider(s, 0xFFE9A3, 0xF2C14E, -0.002f, 18, 1.1f));
        e.registerSpriteSet(ModParticles.VOID_MOTE.get(), s -> AstralParticle.provider(s, 0xB070FF, 0x3A1560, 0.0f, 20, 1.2f));
        e.registerSpriteSet(ModParticles.COMET_TRAIL.get(), s -> AstralParticle.provider(s, 0xFFC56B, 0xB4380C, -0.01f, 16, 1.8f));
    }
}
