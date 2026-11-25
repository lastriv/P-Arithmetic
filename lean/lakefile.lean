import Lake
open Lake DSL

package «PArithmetic» where
  -- Zero external dependencies (uses Lean 4 core only)

@[default_target]
lean_lib «PArithmetic» where
  roots := #[`PArithmetic]
