package com.rimeheart;

import net.minecraftforge.common.ForgeConfigSpec;

/** Server/common tunables. Values are read lazily so they are safe to query at any time. */
public final class Config {
    private static final ForgeConfigSpec.Builder BUILDER = new ForgeConfigSpec.Builder();

    public static final ForgeConfigSpec.DoubleValue BOSS_HEALTH_MULTIPLIER = BUILDER
        .comment("Multiplier for the Frost Sovereign's health (useful for large servers or harder packs).")
        .defineInRange("bossHealthMultiplier", 1.0, 0.1, 20.0);
    public static final ForgeConfigSpec.IntValue SHARDLING_AMBUSH_CHANCE = BUILDER
        .comment("Percent chance that breaking a Rime Crystal Cluster (without Silk Touch) releases a Shardling. 0 disables.")
        .defineInRange("shardlingAmbushChance", 20, 0, 100);
    public static final ForgeConfigSpec.BooleanValue SKIP_EXPERIMENTAL_WARNING = BUILDER
        .comment("Client: skip vanilla's 'Experimental Settings' prompts, which appear for any mod that adds world",
                 "generation through data packs. Equivalent to clicking 'I Know What I'm Doing!' (no backup is made).")
        .define("skipExperimentalWarning", true);

    public static final ForgeConfigSpec SPEC = BUILDER.build();

    private Config() {}

    public static double bossHealthMultiplier() { return safe(() -> BOSS_HEALTH_MULTIPLIER.get(), 1.0); }
    public static int shardlingAmbushChance() { return safe(() -> SHARDLING_AMBUSH_CHANCE.get(), 20); }
    public static boolean skipExperimentalWarning() { return safe(() -> SKIP_EXPERIMENTAL_WARNING.get(), true); }

    private static <T> T safe(java.util.function.Supplier<T> s, T fallback) {
        try {
            return s.get();
        } catch (Throwable t) {
            return fallback;
        }
    }
}
