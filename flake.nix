{
  description = "A fast cubic spline interpolator for real and complex data.";

  inputs = {
    nixpkgs.url = "nixpkgs/nixos-unstable";
    poetry2nix.url = "github:nix-community/poetry2nix";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils, poetry2nix }:
    let
      name = "fcSpline";
    in {
      overlay = nixpkgs.lib.composeManyExtensions [
        poetry2nix.overlay
        (final: prev: {
          blas = prev.blas.override {
            blasProvider = self.mkl;
          };

          ${name} = (prev.poetry2nix.mkPoetryApplication {
            projectDir = ./.;
          });

          "${name}Shell" = (prev.poetry2nix.mkPoetryEnv {
              projectDir = ./.;

              editablePackageSources = {
                ${name} = ./${name};
              };
            });
        })

      ];
    } // (flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
          overlays = [ self.overlay ];
          config.allowUnfree = true;
        };
      in
        rec {
          packages = {
            ${name} = pkgs.${name};
          };

          defaultPackage = packages.${name};
          devShell = pkgs."${name}Shell".env.overrideAttrs (oldAttrs: {
            buildInputs = [ pkgs.poetry pkgs.black pkgs.pyright ];
          });
        }));
}
