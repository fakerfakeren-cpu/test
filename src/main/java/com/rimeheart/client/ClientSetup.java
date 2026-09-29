package com.rimeheart.client;

import com.rimeheart.client.model.ModelDefs;
import com.rimeheart.client.particle.FrostParticle;
import com.rimeheart.client.render.Renderers;
import com.rimeheart.registry.ModEntities;
import com.rimeheart.registry.ModParticles;
import net.minecraft.client.renderer.entity.ThrownItemRenderer;
import net.minecraftforge.client.event.EntityRenderersEvent;
import net.minecraftforge.client.event.RegisterParticleProvidersEvent;
import net.minecraftforge.client.event.ScreenEvent;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext;

/** Client-only registration. Only ever loaded on the physical client. */
public final class ClientSetup {
    private ClientSetup() {}

    public static void init(FMLJavaModLoadingContext context) {
        EntityRenderersEvent.RegisterLayerDefinitions.BUS.addListener(ClientSetup::layers);
        EntityRenderersEvent.RegisterRenderers.BUS.addListener(ClientSetup::renderers);
        RegisterParticleProvidersEvent.BUS.addListener(ClientSetup::particles);
        ScreenEvent.Opening.BUS.addListener(ExperimentalWarningSkipper::onScreenOpening);
        TickEvent.ClientTickEvent.Post.BUS.addListener(ExperimentalWarningSkipper::onClientTick);
        if (ClientTest.enabled()) {
            TickEvent.ClientTickEvent.Post.BUS.addListener(ClientTest::onClientTick);
            ClientTest.startWatchdog();
        }
    }

    private static void layers(EntityRenderersEvent.RegisterLayerDefinitions e) {
        e.registerLayerDefinition(Renderers.WRAITH, ModelDefs::createFrostWraith);
        e.registerLayerDefinition(Renderers.SHARDLING, ModelDefs::createShardling);
        e.registerLayerDefinition(Renderers.SOVEREIGN, ModelDefs::createFrostSovereign);
    }

    private static void renderers(EntityRenderersEvent.RegisterRenderers e) {
        e.registerEntityRenderer(ModEntities.FROST_WRAITH.get(), Renderers.Wraith::new);
        e.registerEntityRenderer(ModEntities.SHARDLING.get(), Renderers.Shardling::new);
        e.registerEntityRenderer(ModEntities.FROST_SOVEREIGN.get(), Renderers.Sovereign::new);
        e.registerEntityRenderer(ModEntities.ICE_SHARD.get(), ctx -> new ThrownItemRenderer<>(ctx, 1.25f, true));
        e.registerEntityRenderer(ModEntities.FROST_CHARGE.get(), ThrownItemRenderer::new);
    }

    private static void particles(RegisterParticleProvidersEvent e) {
        e.registerSpriteSet(ModParticles.FROST_GLINT.get(), s -> FrostParticle.provider(s, 0xD8F6FF, 0x5FC3EE, 0.0f, 14, 1.0f));
        e.registerSpriteSet(ModParticles.SNOW_PUFF.get(), s -> FrostParticle.provider(s, 0xFFFFFF, 0xBFD9EA, 0.004f, 24, 1.6f));
        e.registerSpriteSet(ModParticles.WRAITH_WISP.get(), s -> FrostParticle.provider(s, 0x8FF0E0, 0x1F6E78, -0.004f, 20, 1.2f));
    }
}
