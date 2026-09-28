package com.astralfall;

import com.astralfall.command.AstralfallCommand;
import com.astralfall.entity.boss.AstraeusEntity;
import com.astralfall.entity.boss.BossSummoner;
import com.astralfall.entity.mob.AstralWispEntity;
import com.astralfall.entity.mob.MeteoriteCrawlerEntity;
import com.astralfall.entity.mob.VoidGazerEntity;
import com.astralfall.entity.mob.VoidStalkerEntity;
import com.astralfall.event.ArmorEffects;
import com.astralfall.event.GravityGauntletHandler;
import com.astralfall.event.Starfall;
import com.astralfall.registry.*;
import com.mojang.logging.LogUtils;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.SpawnPlacementTypes;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.event.RegisterCommandsEvent;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.EntityAttributeCreationEvent;
import net.minecraftforge.event.entity.SpawnPlacementRegisterEvent;
import net.minecraftforge.event.entity.living.LivingFallEvent;
import net.minecraftforge.event.server.ServerStartedEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.config.ModConfig;
import net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext;
import net.minecraftforge.fml.loading.FMLEnvironment;
import org.slf4j.Logger;

/**
 * Astralfall — the stars are falling.
 */
@Mod(Astralfall.MODID)
public final class Astralfall {
    public static final String MODID = "astralfall";
    public static final Logger LOGGER = LogUtils.getLogger();

    public Astralfall(FMLJavaModLoadingContext context) {
        var modBus = context.getModBusGroup();
        ModBlocks.BLOCKS.register(modBus);
        ModItems.ITEMS.register(modBus);
        ModEntities.ENTITIES.register(modBus);
        ModSounds.SOUNDS.register(modBus);
        ModParticles.PARTICLES.register(modBus);
        ModWorldgen.STRUCTURE_TYPES.register(modBus);
        ModWorldgen.STRUCTURE_PIECES.register(modBus);
        ModWorldgen.FEATURES.register(modBus);
        ModTabs.TABS.register(modBus);

        context.registerConfig(ModConfig.Type.COMMON, Config.SPEC);

        EntityAttributeCreationEvent.BUS.addListener(Astralfall::attributes);
        SpawnPlacementRegisterEvent.BUS.addListener(Astralfall::spawnPlacements);
        RegisterCommandsEvent.BUS.addListener(e -> AstralfallCommand.register(e.getDispatcher()));
        TickEvent.LevelTickEvent.Post.BUS.addListener(Astralfall::levelTick);
        TickEvent.PlayerTickEvent.Post.BUS.addListener(e -> ArmorEffects.onPlayerTick(e.player()));
        LivingFallEvent.BUS.addListener(ArmorEffects::onFall);
        ServerStartedEvent.BUS.addListener(SelfTest::onServerStarted);
        TickEvent.ServerTickEvent.Post.BUS.addListener(SelfTest::onServerTick);

        if (FMLEnvironment.dist == Dist.CLIENT) {
            com.astralfall.client.ClientSetup.init(context);
        }
    }

    private static void attributes(EntityAttributeCreationEvent event) {
        event.put(ModEntities.ASTRAL_WISP.get(), AstralWispEntity.createAttributes().build());
        event.put(ModEntities.VOID_STALKER.get(), VoidStalkerEntity.createAttributes().build());
        event.put(ModEntities.METEORITE_CRAWLER.get(), MeteoriteCrawlerEntity.createAttributes().build());
        event.put(ModEntities.VOID_GAZER.get(), VoidGazerEntity.createAttributes().build());
        event.put(ModEntities.ASTRAEUS.get(), AstraeusEntity.createAttributes().build());
    }

    private static void spawnPlacements(SpawnPlacementRegisterEvent event) {
        event.register(ModEntities.VOID_STALKER.get(), SpawnPlacementTypes.ON_GROUND, Heightmap.Types.MOTION_BLOCKING_NO_LEAVES,
            Monster::checkMonsterSpawnRules, SpawnPlacementRegisterEvent.Operation.REPLACE);
        event.register(ModEntities.METEORITE_CRAWLER.get(), SpawnPlacementTypes.ON_GROUND, Heightmap.Types.MOTION_BLOCKING_NO_LEAVES,
            Monster::checkMonsterSpawnRules, SpawnPlacementRegisterEvent.Operation.REPLACE);
        event.register(ModEntities.VOID_GAZER.get(), SpawnPlacementTypes.NO_RESTRICTIONS, Heightmap.Types.MOTION_BLOCKING_NO_LEAVES,
            Monster::checkMonsterSpawnRules, SpawnPlacementRegisterEvent.Operation.REPLACE);
        event.register(ModEntities.ASTRAL_WISP.get(), SpawnPlacementTypes.NO_RESTRICTIONS, Heightmap.Types.MOTION_BLOCKING_NO_LEAVES,
            AstralWispEntity::checkWispSpawnRules, SpawnPlacementRegisterEvent.Operation.REPLACE);
    }

    private static void levelTick(TickEvent.LevelTickEvent.Post event) {
        if (event.level() instanceof ServerLevel level) {
            Starfall.tick(level);
            BossSummoner.tick(level);
            GravityGauntletHandler.tick(level);
        }
    }
}
