{
  description = "Plant Phase Manager development environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
        python = pkgs.python3;
      in {
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            python
            python.pkgs.customtkinter
            python.pkgs.python-dateutil
            python.pkgs.python-dotenv
            tkinter
          ];

          shellHook = ''
            echo "Plant Phase Manager development environment"
            echo "Python: $(python --version)"
          '';
        };
      });
}
