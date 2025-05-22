let
  # Stable and unstable nixpkgs
  stablePkgs = import <nixpkgs> {};
  unstablePkgs = import (builtins.fetchTarball {
    url = "https://github.com/NixOS/nixpkgs/archive/nixos-unstable.tar.gz";
  }) {};

  inherit (stablePkgs) lib;

  pyproject-nix = import (builtins.fetchGit {
    url = "https://github.com/pyproject-nix/pyproject.nix.git";
  }) {
    inherit lib;
  };

  uv2nix = import (builtins.fetchGit {
    url = "https://github.com/pyproject-nix/uv2nix.git";
  }) {
    inherit pyproject-nix lib;
  };

  pyproject-build-systems = import (builtins.fetchGit {
    url = "https://github.com/pyproject-nix/build-system-pkgs.git";
  }) {
    inherit pyproject-nix uv2nix lib;
  };

in stablePkgs.mkShell {
  packages = with stablePkgs; [
    python310
    python311
    python312
    python313
    unstablePkgs.uv
    unstablePkgs.ruff
  ];

  shellHook = ''
    export TMPDIR=/tmp
    export RUFF_PATH=$(which ruff)
    echo "Shell with multiple Python versions, uv (from unstable), and uv2nix tooling."
  '';
}
