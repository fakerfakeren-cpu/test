package com.oathbound;

import com.mojang.logging.LogUtils;
import com.oathbound.command.OathboundCommand;
import com.oathbound.entity.boss.*;
import com.oathbound.entity.mob.*;
import com.oathbound.event.GameEvents;
import com.oathbound.event.GateRite;
import com.oathbound.quest.QuestLog;
import com.oathbound.registry.*;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.SpawnPlacementTypes;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.ComposterBlock;
import net.minecraft.world.level.block.FlowerPotBlock;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.event.RegisterCommandsEvent;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.EntityAttributeCreationEvent;
import net.minecraftforge.event.entity.SpawnPlacementRegisterEvent;
import net.minecraftforge.event.entity.living.LivingHurtEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.event.server.ServerStartedEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.config.ModConfig;
import net.minecraftforge.fml.event.lifecycle.FMLCommonSetupEvent;
import net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext;
import net.minecraftforge.fml.loading.FMLEnvironment;
import org.slf4j.Logger;

/**
 * Oathbound: The Hollow Crown. The last squire of the Lanternguard wins back three Oath Seals from the
 * hollowed keepers of a fallen order, opens the Sundered Gate and breaks the crown of the king who lied.
 */
@Mod(Oathbound.MODID)
public final class Oathbound {
    public static final String MODID = "oathbound";
    public static final Logger LOGGER = LogUtils.getLogger();

    public Oathbound(FMLJavaModLoadingContext context) {
        var modBus = context.getModBusGroup();
        ModBlocks.BLOCKS.register(modBus);
        ModItems.ITEMS.register(modBus);
        ModEntities.ENTITIES.register(modBus);
        ModSounds.SOUNDS.register(modBus);
        ModParticles.PARTICLES.register(modBus);
        ModEffects.EFFECTS.register(modBus);
        ModWorldgen.STRUCTURE_TYPES.register(modBus);
        ModWorldgen.STRUCTURE_PIECES.register(modBus);
        ModWorldgen.FEATURES.register(modBus);
        ModTabs.TABS.register(modBus);

        context.registerConfig(ModConfig.Type.COMMON, Config.SPEC);
        FMLCommonSetupEvent.getBus(modBus).addListener(Oathbound::commonSetup);

        EntityAttributeCreationEvent.BUS.addListener(Oathbound::attributes);
        SpawnPlacementRegisterEvent.BUS.addListener(Oathbound::spawnPlacements);
        RegisterCommandsEvent.BUS.addListener(e -> OathboundCommand.register(e.getDispatcher()));
        RegisterCommandsEvent.BUS.addListener(e -> QuestLog.register(e.getDispatcher()));
        TickEvent.LevelTickEvent.Post.BUS.addListener(Oathbound::levelTick);
        TickEvent.PlayerTickEvent.Post.BUS.addListener(e -> GameEvents.onPlayerTick(e.player()));
        LivingHurtEvent.BUS.addListener(GameEvents::onLivingHurt);
        PlayerEvent.PlayerLoggedInEvent.BUS.addListener(GameEvents::onLogin);
        PlayerEvent.PlayerChangedDimensionEvent.BUS.addListener(GameEvents::onChangedDimension);
        ServerStartedEvent.BUS.addListener(SelfTest::onServerStarted);
        TickEvent.ServerTickEvent.Post.BUS.addListener(SelfTest::onServerTick);

        if (FMLEnvironment.dist == Dist.CLIENT) {
            com.oathbound.client.ClientSetup.init(context);
        }
    }

    /** Potted plants and compost: both are vanilla lookup tables that mods fill once registries are frozen. */
    private static void commonSetup(FMLCommonSetupEvent event) {
        event.enqueueWork(() -> {
            FlowerPotBlock pot = (FlowerPotBlock) Blocks.FLOWER_POT;
            pot.addPlant(ModBlocks.DUSK_LILY.getId(), ModBlocks.POTTED_DUSK_LILY);
            pot.addPlant(ModBlocks.EMBERROOT.getId(), ModBlocks.POTTED_EMBERROOT);
            pot.addPlant(ModBlocks.MOONPETAL.getId(), ModBlocks.POTTED_MOONPETAL);
            pot.addPlant(ModBlocks.GLOAM_FERN.getId(), ModBlocks.POTTED_GLOAM_FERN);
            pot.addPlant(ModBlocks.VEILBLOOM.getId(), ModBlocks.POTTED_VEILBLOOM);
            pot.addPlant(ModBlocks.GLOAMWOOD_SAPLING.getId(), ModBlocks.POTTED_GLOAMWOOD_SAPLING);
            for (var plant : java.util.List.of(ModBlocks.DUSK_LILY, ModBlocks.EMBERROOT, ModBlocks.MOONPETAL, ModBlocks.VEILBLOOM,
                ModBlocks.GLOAM_FERN, ModBlocks.GLOAMWOOD_SAPLING, ModBlocks.GLOAMWOOD_LEAVES)) {
                ComposterBlock.COMPOSTABLES.put(plant.get().asItem(), 0.3f);
            }
            ComposterBlock.COMPOSTABLES.put(ModBlocks.GLIMMER_MOSS.get().asItem(), 0.3f);
        });
    }

    private static void attributes(EntityAttributeCreationEvent event) {
        event.put(ModEntities.LANTERNMOTH.get(), LanternmothEntity.createAttributes().build());
        event.put(ModEntities.GLOAMLING.get(), GloamlingEntity.createAttributes().build());
        event.put(ModEntities.FORSWORN_KNIGHT.get(), ForswornKnightEntity.createAttributes().build());
        event.put(ModEntities.BARROW_WIGHT.get(), BarrowWightEntity.createAttributes().build());
        event.put(ModEntities.ANIMATED_TOME.get(), AnimatedTomeEntity.createAttributes().build());
        event.put(ModEntities.VEILHOUND.get(), VeilhoundEntity.createAttributes().build());
        event.put(ModEntities.SPECTRAL_HOUSECARL.get(), SpectralHousecarlEntity.createAttributes().build());
        event.put(ModEntities.SIR_CALDRIS.get(), SirCaldrisEntity.createAttributes().build());
        event.put(ModEntities.ARCHMAGE_VEYL.get(), ArchmageVeylEntity.createAttributes().build());
        event.put(ModEntities.HRODGAR.get(), HrodgarEntity.createAttributes().build());
        event.put(ModEntities.MORVANE.get(), MorvaneEntity.createAttributes().build());
        RosterRegistry.attributes(event);
    }

    private static void spawnPlacements(SpawnPlacementRegisterEvent event) {
        var ground = SpawnPlacementTypes.ON_GROUND;
        var surface = Heightmap.Types.MOTION_BLOCKING_NO_LEAVES;
        event.register(ModEntities.GLOAMLING.get(), ground, surface, Monster::checkMonsterSpawnRules, SpawnPlacementRegisterEvent.Operation.REPLACE);
        event.register(ModEntities.FORSWORN_KNIGHT.get(), ground, surface, Monster::checkMonsterSpawnRules, SpawnPlacementRegisterEvent.Operation.REPLACE);
        event.register(ModEntities.VEILHOUND.get(), ground, surface, Monster::checkAnyLightMonsterSpawnRules, SpawnPlacementRegisterEvent.Operation.REPLACE);
        event.register(ModEntities.BARROW_WIGHT.get(), ground, surface, Monster::checkMonsterSpawnRules, SpawnPlacementRegisterEvent.Operation.REPLACE);
        event.register(ModEntities.LANTERNMOTH.get(), SpawnPlacementTypes.NO_RESTRICTIONS, surface,
            LanternmothEntity::checkMothSpawnRules, SpawnPlacementRegisterEvent.Operation.REPLACE);
        RosterRegistry.spawnPlacements(event);
    }

    private static void levelTick(TickEvent.LevelTickEvent.Post event) {
        if (event.level() instanceof ServerLevel level) {
            GateRite.tick(level);
            GameEvents.levelTick(level);
        }
    }
}
