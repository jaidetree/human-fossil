{
  description = "Human Fossil";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            python313
            uv

            nodejs_24

            # PostgreSQL
            postgresql_18
            pgcli
            postgresql_18.lib
            openssl
          ];

          # Shell hook for additional environment setup
          shellHook = ''
            echo "Python development environment loaded!"
            echo "Python version: $(python3 --version)"
            echo "uv version: $(uv --version)"
            echo "Postgres version: $(postgres --version)"
          '';
        };
      }
    );
}
