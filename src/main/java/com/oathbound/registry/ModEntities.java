package com.oathbound.registry;

import com.oathbound.Oathbound;
import com.oathbound.entity.boss.*;
import com.oathbound.entity.mob.*;
import com.oathbound.entity.projectile.*;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobCategory;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

import java.util.function.UnaryOperator;

public final class ModEntities {
    public static final DeferredRegister<EntityType<?>> ENTITIES = DeferredRegister.create(ForgeRegistries.ENTITY_TYPES, Oathbound.MODID);

    // ------------------------------------------------------------------ creatures
    public static final RegistryObject<EntityType<LanternmothEntity>> LANTERNMOTH = reg("lanternmoth", LanternmothEntity::new, MobCategory.AMBIENT,
        b -> b.sized(0.5f, 0.45f).clientTrackingRange(8));
    public static final RegistryObject<EntityType<GloamlingEntity>> GLOAMLING = reg("gloamling", GloamlingEntity::new, MobCategory.MONSTER,
        b -> b.sized(0.6f, 0.95f).clientTrackingRange(8));
    public static final RegistryObject<EntityType<ForswornKnightEntity>> FORSWORN_KNIGHT = reg("forsworn_knight", ForswornKnightEntity::new, MobCategory.MONSTER,
        b -> b.sized(0.7f, 2.1f).clientTrackingRange(10));
    public static final RegistryObject<EntityType<BarrowWightEntity>> BARROW_WIGHT = reg("barrow_wight", BarrowWightEntity::new, MobCategory.MONSTER,
        b -> b.sized(0.7f, 2.0f).clientTrackingRange(10));
    public static final RegistryObject<EntityType<AnimatedTomeEntity>> ANIMATED_TOME = reg("animated_tome", AnimatedTomeEntity::new, MobCategory.MONSTER,
        b -> b.sized(0.7f, 0.5f).clientTrackingRange(8));
    public static final RegistryObject<EntityType<VeilhoundEntity>> VEILHOUND = reg("veilhound", VeilhoundEntity::new, MobCategory.MONSTER,
        b -> b.sized(0.9f, 1.05f).clientTrackingRange(10));
    public static final RegistryObject<EntityType<SpectralHousecarlEntity>> SPECTRAL_HOUSECARL = reg("spectral_housecarl", SpectralHousecarlEntity::new, MobCategory.MISC,
        b -> b.sized(0.7f, 2.0f).clientTrackingRange(10).fireImmune());

    // ------------------------------------------------------------------ keepers & the king
    public static final RegistryObject<EntityType<SirCaldrisEntity>> SIR_CALDRIS = reg("sir_caldris", SirCaldrisEntity::new, MobCategory.MONSTER,
        b -> b.sized(1.0f, 2.6f).clientTrackingRange(12));
    public static final RegistryObject<EntityType<ArchmageVeylEntity>> ARCHMAGE_VEYL = reg("archmage_veyl", ArchmageVeylEntity::new, MobCategory.MONSTER,
        b -> b.sized(0.8f, 2.3f).clientTrackingRange(12).fireImmune());
    public static final RegistryObject<EntityType<HrodgarEntity>> HRODGAR = reg("hrodgar", HrodgarEntity::new, MobCategory.MONSTER,
        b -> b.sized(1.6f, 3.9f).clientTrackingRange(12));
    public static final RegistryObject<EntityType<MorvaneEntity>> MORVANE = reg("morvane", MorvaneEntity::new, MobCategory.MONSTER,
        b -> b.sized(1.2f, 3.3f).clientTrackingRange(16).fireImmune());

    // ------------------------------------------------------------------ spell effects
    public static final RegistryObject<EntityType<com.oathbound.entity.SpellMarkEntity>> SPELL_MARK = reg("spell_mark", com.oathbound.entity.SpellMarkEntity::new, MobCategory.MISC,
        b -> b.sized(0.2f, 0.2f).clientTrackingRange(16).updateInterval(20).noSave().fireImmune().noSummon());

    // ------------------------------------------------------------------ projectiles
    public static final RegistryObject<EntityType<ArcaneOrbEntity>> ARCANE_ORB = reg("arcane_orb", ArcaneOrbEntity::new, MobCategory.MISC,
        b -> b.sized(0.6f, 0.6f).clientTrackingRange(10).updateInterval(1).noSave());
    public static final RegistryObject<EntityType<GlyphBoltEntity>> GLYPH_BOLT = reg("glyph_bolt", GlyphBoltEntity::new, MobCategory.MISC,
        b -> b.sized(0.35f, 0.35f).clientTrackingRange(8).updateInterval(1).noSave());
    public static final RegistryObject<EntityType<GloamBoltEntity>> GLOAM_BOLT = reg("gloam_bolt", GloamBoltEntity::new, MobCategory.MISC,
        b -> b.sized(0.45f, 0.45f).clientTrackingRange(10).updateInterval(1).noSave());
    public static final RegistryObject<EntityType<CrownBladeEntity>> CROWN_BLADE = reg("crown_blade", CrownBladeEntity::new, MobCategory.MISC,
        b -> b.sized(0.5f, 0.5f).clientTrackingRange(10).updateInterval(1).noSave());
    public static final RegistryObject<EntityType<AnchorHookEntity>> ANCHOR_HOOK = reg("anchor_hook", AnchorHookEntity::new, MobCategory.MISC,
        b -> b.sized(0.5f, 0.5f).clientTrackingRange(8).updateInterval(1).noSave());
    public static final RegistryObject<EntityType<SunArrowEntity>> SUN_ARROW = reg("sun_arrow", SunArrowEntity::new, MobCategory.MISC,
        b -> b.sized(0.3f, 0.3f).clientTrackingRange(8).updateInterval(1).noSave());
    public static final RegistryObject<EntityType<LumenFlaskEntity>> LUMEN_FLASK = reg("lumen_flask", LumenFlaskEntity::new, MobCategory.MISC,
        b -> b.sized(0.25f, 0.25f).clientTrackingRange(4).updateInterval(10));

    private static <T extends Entity> RegistryObject<EntityType<T>> reg(String name, EntityType.EntityFactory<T> factory, MobCategory category,
                                                                        UnaryOperator<EntityType.Builder<T>> props) {
        return ENTITIES.register(name, () -> props.apply(EntityType.Builder.of(factory, category)).build(ENTITIES.key(name)));
    }

    private ModEntities() {}
}
