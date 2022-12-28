// Source header
#include "Compile.hpp"

#include "clang/Frontend/TextDiagnosticPrinter.h"
#include "clang/CodeGen/CodeGenAction.h"

#include "clang/Lex/Preprocessor.h"
#include "clang/Lex/PreprocessorOptions.h"
#include "llvm/IR/Module.h"

namespace QED { namespace Pragmatic
{
	bool Compile(clang::CompilerInvocation& compilerInvocation)
	{
		llvm::raw_ostream &errs = llvm::errs();
		auto compiler = std::make_unique<clang::CompilerInstance>();
		auto invocation = std::make_shared<clang::CompilerInvocation>(compilerInvocation);
		auto diags = llvm::makeIntrusiveRefCnt<clang::DiagnosticIDs>();
		auto diag_options = llvm::makeIntrusiveRefCnt<clang::DiagnosticOptions>();
		auto diag_printer = std::make_unique<clang::TextDiagnosticPrinter>(errs, diag_options.get());

		// allocate via new, ownership is transferred to compiler instance
		auto diag_engine = new clang::DiagnosticsEngine(diags, diag_options);
		diag_engine->setClient(diag_printer.get(), false);

		// Setup compiler
		compiler->setInvocation(invocation);
		compiler->setDiagnostics(diag_engine);
		auto action = std::unique_ptr<clang::CodeGenAction>(new clang::EmitObjAction());

		// Compile
		compiler->ExecuteAction(*action);

		return static_cast<bool>(action->takeModule());
	}

	RecompileConsumer::RecompileConsumer(clang::CompilerInstance& CI) : CI(CI)
	{
		
	}

	void RecompileConsumer::HandleTranslationUnit(clang::ASTContext& context)
	{
		llvm::errs() << "Should recompile : " << (PragmaHandler::ShouldRecompile() ? "true" : "false") << '\n';

		if (PragmaHandler::ShouldRecompile())
		{
			PragmaHandler::ResetRecompile();

			CI.createDiagnostics();

			auto& invocation = CI.getInvocation();
			invocation.getLangOpts()->LangStd = clang::LangStandard::Kind::lang_cxx17;
			invocation.getLangOpts()->CPlusPlus17 = 1;
			//invocation.getLangOpts()->setLangDefaults
			invocation.getFrontendOpts().OutputFile = "new.o";

			bool result = Compile(invocation);

			llvm::errs() << "Recompile result : " << (result ? "true" : "false") << '\n';
		}
	}

	std::unique_ptr<clang::ASTConsumer> RecompileAction::CreateASTConsumer(clang::CompilerInstance &CI, llvm::StringRef)
	{
		return std::make_unique<RecompileConsumer>(CI);
	}

	bool RecompileAction::ParseArgs(const clang::CompilerInstance &CI, const std::vector<std::string> &args)
	{
		return true;
	}

	clang::PluginASTAction::ActionType RecompileAction::getActionType()
	{
		return AddAfterMainAction;
	}

}} // namespace QED::Pragmatic